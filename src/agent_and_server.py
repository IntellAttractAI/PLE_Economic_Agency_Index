from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

try:
    from smol_agents import Agent, Tool
except Exception:
    # fallback stubs if smol_agents is missing
    class Tool:
        pass
    class Agent:
        def __init__(self, tools=None):
            self.tools = tools or []
        def run(self, question: str):
            return "Agent unavailable"

data = None
try:
    data = pd.read_parquet("data/eai.parquet")
except Exception:
    data = pd.DataFrame()

def compute_z(county_fips: str, year: int) -> float:
    subset = data[data['year'] == year]
    if subset.empty:
        return float('nan')
    mean = subset['eai'].mean()
    std = subset['eai'].std()
    val = subset[subset['fips'] == county_fips]['eai'].iloc[0]
    return (val - mean) / std

class ComputeZTool(Tool):
    name = "compute_z"
    description = "Compute the z-score of EAI for a county and year"
    def run(self, county_fips: str, year: int):
        return compute_z(county_fips, year)

agent = Agent(tools=[ComputeZTool()])
app = FastAPI()

class Query(BaseModel):
    question: str

@app.post("/agent")
def ask_agent(q: Query):
    return {"answer": agent.run(q.question)}
