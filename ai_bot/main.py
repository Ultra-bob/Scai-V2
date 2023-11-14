from pynng import Pair1, Message
from json import loads, dumps
import openai
from dotenv import load_dotenv
import trio

load_dotenv("/run/secrets/dotenv")
oai = openai.AsyncOpenAI()

dumpb = lambda data: dumps(data).encode()

AI_INSTRUCTIONS = "You are an AI designed to answer questions about the videogame Star Citizen. Information that is potentially relevant to the user query is in the message below. Use it if it's relevant, but if there is no relevant information simply tell the user"

async def handle_request(msg: Message):
    data = loads(msg.bytes)
    if not data.get("query"):
        return dumpb({"error": "Invalid request"})
    query = data["query"]
    
    await msg.pipe.asend(dumpb({"update": "Searching"}))

    with Pair1(dial="tcp://database-api:8000", polyamorous=True) as db:
        await db.asend(dumpb({"search": query}))
        response = loads((await db.arecv_msg()).bytes)["result"]
        print(response)
        query_result = "\n\n---\n\n".join([page["content"].strip() for page in response])


    await msg.pipe.asend(dumpb({"update": "Generating Response"}))

    completion = await oai.chat.completions.create(model="gpt-3.5-turbo-1106", messages=[
        {"role": "system", "content": AI_INSTRUCTIONS, "name": "instructions"},
        {"role": "system", "content": query_result, "name": "background_info"},
        {"role": "user", "content": query}
    ])

    await msg.pipe.asend(dumpb({"result": completion.choices[0].message.content}))
    
async def main():
    async with trio.open_nursery() as nursery:
        with Pair1(listen="tcp://0.0.0.0:8000", polyamorous=True) as s:
            print("Listening!")
            while True:
                msg = await s.arecv_msg()
                print("Starting New Task!")
                nursery.start_soon(handle_request, msg)

trio.run(main)