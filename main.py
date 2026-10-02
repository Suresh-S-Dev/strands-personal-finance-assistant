from strands import Agent

agent = Agent(
    model="nvidia.nemotron-nano-3-30b"
)
response = agent("What is an agent harness, in one sentence?")
print(response.message)
