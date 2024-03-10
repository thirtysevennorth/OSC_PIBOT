#!/usr/bin/env python3
import asyncio

# This is your list of coroutines
command_q = []

async def continuously_execute_command_q():
    while True:
        # Process each coroutine in the list
        while command_q:
            command = command_q.pop(0)
            await command

        # Optionally, add a small delay to prevent this loop from hogging CPU
        await asyncio.sleep(0.1)

# # Example of adding coroutines to the list
# coroutines_list.append(move())
# coroutines_list.append(wait(5))
# coroutines_list.append(move())

# # Start the event loop and the coroutine processor
# asyncio.run(process_coroutines())
