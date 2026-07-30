import importlib.metadata
la = importlib.metadata.metadata('langchain-mcp-adapters')
print('langchain-mcp-adapters requires:')
for r in la.get_all('Requires-Dist') or []:
    print(' ', r)
