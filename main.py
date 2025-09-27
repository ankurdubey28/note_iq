from fastapi import FastAPI
import logging
import inngest
import inngest.fast_api
from inngest.experimental import ai
from dotenv import load_dotenv
import uuid
import os
import datetime
from data_loader import load_and_chunk_pdf,embed_texts
from vector_db import QdrantStorage
from custom_types import *

load_dotenv()

inngest_client=inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer()
)

@inngest_client.create_function(
    fn_id="RAG:Inngest PDF",
    trigger=inngest.TriggerEvent(event="rag/inngest_pdf"), # when this event is triggered , then the above inngest funciton is run
    rate_limit=inngest.RateLimit(
    limit=1,
        period=datetime.timedelta(hours=2),
        key="event.rag.upload"

)
)
async def rag_inngest_pdf(ctx:inngest.Context):
    def _load(ctx:inngest.Context)->RAGChunkAndSrc:
        pdf_path=ctx.event.data['pdf_path']
        source_id=ctx.event.data.get("source_id",pdf_path)
        chunks=load_and_chunk_pdf(pdf_path)
        return RAGChunkAndSrc(chunks=chunks, source_id=source_id)

    def _upsert(chunks_and_src:RAGChunkAndSrc)->RAGUpsertResult:
        chunks=chunks_and_src.chunks
        source_id=chunks_and_src.source_id
        vectors=embed_texts(chunks)
        ids=[str(uuid.uuid5(uuid.NAMESPACE_URL,f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads=[{"source":source_id,"text":chunks[i]} for i in range(len(chunks))]
        QdrantStorage().upsert(ids,vectors,payloads)
        return RAGUpsertResult(ingested=len(chunks))

    chunks_and_src=await ctx.step.run("load-and-chunk",lambda: _load(ctx),output_type=RAGChunkAndSrc)
    ingested=await ctx.step.run("embed-and-upsert",lambda: _upsert(chunks_and_src),output_type=RAGUpsertResult)
    return ingested.model_dump()

@inngest_client.create_function(
    fn_id="RAG:Query PDF",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai"),
    rate_limit=inngest.RateLimit(
        limit=5,
        period=datetime.timedelta(hours=1),
        key="event.rag.query"
    )
)
async def rag_query_pdf_ai(ctx:inngest.Context)->RAGSearchResults:
    def _search(query:str,top_k:int=5):
        query_vec=embed_texts([query])[0]
        store=QdrantStorage()
        found=store.search(query_vec,top_k)
        return RAGSearchResults(contexts=found["contexts"],sources=found["sources"])

    query=ctx.event.data["query"]
    top_k=int(ctx.event.data.get("top_k",5))

    found=await ctx.step.run("embed-and-search",lambda :_search(query,top_k),output_type=RAGSearchResults)
    context_block="\n\n".join(f"-{c}" for c in found.contexts)
    user_block=(
        "Use the following context to answer the question \n\n"
        f"Context:\n{context_block}\n\n"
        f"Query:\n{query}\n"
        "Answer concisely using the context above"
        "In case general questions are asked which u can answer yourself and answer it yourself"
    )
    adapter=ai.openai.Adapter(
        auth_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )
    res=await ctx.step.ai.infer(
        "llm-answer",
        adapter=adapter,
        body={
            "max_tokens":1024,
            "temperature":0.2,
            "messages":[
                {"role":"system","content":"you answer question using only the provided context"},
                {"role":"user","content":user_block}
            ]
        }
    )
    ans=res['choices'][0]['message']['content'].strip()
    return {"answer":ans,"sources":found.sources,"num_contexts":len(found.contexts)}

app=FastAPI()



inngest.fast_api.serve(app,inngest_client,[rag_inngest_pdf,rag_query_pdf_ai])
