from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

frontendHost = "http://localhost:3000"

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontendHost],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Node(BaseModel):
    id: str

class Edge(BaseModel):
    source: str
    target: str

class PipelineRequest(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

def detect_cycle(nodes, edges):
    # Create adjacency list representation of the graph
    adjacency_list = {}
    for node in nodes:
        adjacency_list[node.id] = []
    
    for edge in edges:
        adjacency_list[edge.source].append(edge.target)
    
    # Function to perform DFS and detect cycles
    def dfs(node, visited, recursion_stack):
        visited[node] = True
        recursion_stack[node] = True
        
        for neighbor in adjacency_list.get(node, []):
            if not visited.get(neighbor, False):
                if dfs(neighbor, visited, recursion_stack):
                    return True
            elif recursion_stack.get(neighbor, False):
                return True
        
        recursion_stack[node] = False
        return False
    
    # Initialize data structures for DFS
    visited = {node.id: False for node in nodes}
    
    # Perform DFS from each node to detect cycles
    for node_id in adjacency_list:
        if not visited[node_id]:
            recursion_stack = {node.id: False for node in nodes}
            if dfs(node_id, visited, recursion_stack):
                return True
    
    return False

@app.post('/pipelines/parse')
async def pipe(pipeline: PipelineRequest):
    try:
        # Detect cycles in the graph
        is_dag = not detect_cycle(pipeline.nodes, pipeline.edges)
        
        return {
            "num_nodes": len(pipeline.nodes),
            "num_edges": len(pipeline.edges),
            "is_dag": is_dag
        }
    except Exception as e:
        # Log the exception for debugging
        print(f"Exception occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
