"""
EXAMPLE IMPLEMENTATION: Advanced RAG Patterns from LangGraph

File này demonstrate các patterns học từ LangGraph áp dụng cho ATTECH RAG.
Có thể chạy trực tiếp để test các concepts.
"""

from typing import TypedDict, Annotated, List, Optional, Dict, Any
from typing_extensions import Literal
from datetime import datetime
from enum import Enum
import operator
import time
import json

# ============================================================================
# 1. STATE MANAGEMENT PATTERN
# ============================================================================

class RAGStage(str, Enum):
    """Các giai đoạn của RAG pipeline"""
    INIT = "init"
    QUERY_EXPANSION = "query_expansion"
    RETRIEVAL = "retrieval"
    GRADING = "grading"
    REWRITING = "rewriting"
    GENERATION = "generation"
    VALIDATION = "validation"
    COMPLETED = "completed"
    FAILED = "failed"

class LegalDocument(TypedDict):
    """Cấu trúc tài liệu pháp luật"""
    document_id: str
    legal_code: str
    title: str
    content: str
    relevance_score: float

class ATTECHRAGState(TypedDict):
    """State cho hệ thống RAG ATTECH"""
    # Input
    question: str
    user_id: str
    session_id: str
    
    # Processing state
    stage: RAGStage
    expanded_queries: List[str]
    documents: Annotated[List[LegalDocument], operator.add]
    filtered_documents: List[LegalDocument]
    
    # Generation
    generation: str
    citations: List[str]
    
    # Control flow
    loop_count: Annotated[int, operator.add]
    max_loops: int
    retry_count: Annotated[int, operator.add]
    
    # Quality metrics
    relevance_score: Optional[float]
    confidence_score: Optional[float]
    hallucination_detected: bool
    
    # Metadata
    timestamp: datetime
    processing_time: float
    errors: Annotated[List[str], operator.add]

def merge_rag_state(current: ATTECHRAGState, update: dict) -> ATTECHRAGState:
    """Merge state updates - học từ LangGraph state reducer"""
    new_state = current.copy()
    
    for key, value in update.items():
        if key not in new_state:
            new_state[key] = value
            continue
            
        # Handle Annotated types with operators
        annotations = ATTECHRAGState.__annotations__.get(key)
        
        if hasattr(annotations, '__metadata__'):
            # Có operator (e.g., operator.add)
            op = annotations.__metadata__[0]
            current_value = current.get(key)
            
            # Initialize nếu chưa có
            if current_value is None:
                if isinstance(value, list):
                    current_value = []
                elif isinstance(value, int):
                    current_value = 0
                else:
                    current_value = type(value)()
            
            new_state[key] = op(current_value, value)
        else:
            # Override thông thường
            new_state[key] = value
    
    return new_state

# ============================================================================
# 2. GRAPH EXECUTION PATTERN (Pregel Algorithm)
# ============================================================================

from typing import Callable

class RAGNode:
    """Node trong RAG graph"""
    def __init__(
        self,
        name: str,
        func: Callable[[ATTECHRAGState], dict],
        subscribes_to: List[RAGStage] = None
    ):
        self.name = name
        self.func = func
        self.subscribes_to = subscribes_to or []
    
    def should_execute(self, state: ATTECHRAGState) -> bool:
        """Check nếu node cần execute ở stage hiện tại"""
        return state["stage"] in self.subscribes_to
    
    def execute(self, state: ATTECHRAGState) -> dict:
        """Execute node function"""
        try:
            print(f"  → Executing node: {self.name}")
            return self.func(state)
        except Exception as e:
            print(f"  ✗ Error in {self.name}: {str(e)}")
            return {"errors": [f"Error in {self.name}: {str(e)}"]}

class RAGGraph:
    """Graph executor học từ Pregel algorithm"""
    def __init__(self, max_iterations: int = 10):
        self.nodes: Dict[str, RAGNode] = {}
        self.max_iterations = max_iterations
    
    def add_node(self, node: RAGNode):
        """Add node vào graph"""
        self.nodes[node.name] = node
        print(f"Added node: {node.name} (subscribes to: {node.subscribes_to})")
    
    def _plan_phase(self, state: ATTECHRAGState) -> List[RAGNode]:
        """PHASE 1: PLAN - Xác định nodes nào cần execute"""
        executable_nodes = []
        for node in self.nodes.values():
            if node.should_execute(state):
                executable_nodes.append(node)
        return executable_nodes
    
    def _execute_phase(self, nodes: List[RAGNode], state: ATTECHRAGState) -> List[dict]:
        """PHASE 2: EXECUTE - Chạy nodes"""
        results = []
        for node in nodes:
            result = node.execute(state)
            results.append(result)
        return results
    
    def _update_phase(self, state: ATTECHRAGState, results: List[dict]) -> ATTECHRAGState:
        """PHASE 3: UPDATE - Merge updates vào state"""
        new_state = state
        for result in results:
            new_state = merge_rag_state(new_state, result)
        return new_state
    
    def execute(self, initial_state: ATTECHRAGState, debug: bool = True) -> ATTECHRAGState:
        """Execute graph với Pregel algorithm"""
        state = initial_state
        iteration = 0
        
        print(f"\n{'='*70}")
        print(f"STARTING GRAPH EXECUTION")
        print(f"Initial question: {state['question']}")
        print(f"Initial stage: {state['stage']}")
        print(f"{'='*70}\n")
        
        while iteration < self.max_iterations:
            if debug:
                print(f"\n--- Iteration {iteration + 1} ---")
                print(f"Current stage: {state['stage']}")
            
            # PHASE 1: PLAN
            executable_nodes = self._plan_phase(state)
            
            if not executable_nodes:
                if debug:
                    print("No more nodes to execute. Stopping.")
                break
            
            if debug:
                print(f"Executing {len(executable_nodes)} node(s)...")
            
            # PHASE 2: EXECUTE
            start_time = time.time()
            results = self._execute_phase(executable_nodes, state)
            execution_time = time.time() - start_time
            
            if debug:
                print(f"Execution time: {execution_time:.3f}s")
            
            # PHASE 3: UPDATE
            state = self._update_phase(state, results)
            state = merge_rag_state(state, {"processing_time": execution_time})
            
            # Check termination
            if state["stage"] == RAGStage.COMPLETED:
                if debug:
                    print("✓ Reached COMPLETED stage. Stopping.")
                break
            
            if state["stage"] == RAGStage.FAILED:
                if debug:
                    print("✗ Reached FAILED stage. Stopping.")
                break
            
            if state["loop_count"] >= state["max_loops"]:
                if debug:
                    print(f"✗ Max loops ({state['max_loops']}) reached. Stopping.")
                state = merge_rag_state(state, {
                    "errors": ["Max loops reached"],
                    "stage": RAGStage.FAILED
                })
                break
            
            iteration += 1
        
        if debug:
            print(f"\n{'='*70}")
            print(f"EXECUTION COMPLETE")
            print(f"Final stage: {state['stage']}")
            print(f"Total iterations: {iteration + 1}")
            print(f"Total processing time: {state['processing_time']:.3f}s")
            print(f"Documents found: {len(state['documents'])}")
            print(f"Errors: {len(state['errors'])}")
            print(f"{'='*70}\n")
        
        return state

# ============================================================================
# 3. RAG NODES IMPLEMENTATION
# ============================================================================

def query_expansion_node(state: ATTECHRAGState) -> dict:
    """Node 1: Query expansion"""
    question = state["question"]
    
    # Simulate query expansion với patterns
    expanded = [
        question,  # Original
        question + " quy định",  # Pattern 1
        question + " luật",  # Pattern 2
    ]
    
    # Thêm entity extraction
    if "điều" in question.lower():
        expanded.append(question.replace("Điều", "Article"))
    
    print(f"    Expanded to {len(expanded)} queries")
    
    return {
        "expanded_queries": expanded,
        "stage": RAGStage.RETRIEVAL,
        "loop_count": 1
    }

def retrieval_node(state: ATTECHRAGState) -> dict:
    """Node 2: Document retrieval"""
    queries = state.get("expanded_queries", [state["question"]])
    
    # Simulate retrieval (trong thực tế: ChromaDB + PostgreSQL)
    mock_docs = [
        {
            "document_id": f"doc_{i}",
            "legal_code": f"95/202{i}/NĐ-CP",
            "title": f"Nghị định {i}",
            "content": f"Nội dung tài liệu {i}...",
            "relevance_score": 0.9 - (i * 0.1)
        }
        for i in range(3)
    ]
    
    print(f"    Retrieved {len(mock_docs)} documents")
    
    return {
        "documents": mock_docs,
        "stage": RAGStage.GRADING,
        "loop_count": 1
    }

def grading_node(state: ATTECHRAGState) -> dict:
    """Node 3: Document grading với conditional routing"""
    docs = state.get("documents", [])
    retry_count = state.get("retry_count", 0)
    
    # Grade documents
    threshold = 0.7
    filtered = [d for d in docs if d["relevance_score"] >= threshold]
    
    print(f"    Graded {len(docs)} docs → {len(filtered)} passed (threshold={threshold})")
    
    # Conditional routing
    if not filtered and retry_count < 2:
        print(f"    → No relevant docs, retry {retry_count + 1}/2")
        return {
            "filtered_documents": [],
            "stage": RAGStage.REWRITING,
            "retry_count": 1,
            "loop_count": 1
        }
    elif not filtered and retry_count >= 2:
        print(f"    → Max retries reached, failing")
        return {
            "filtered_documents": [],
            "stage": RAGStage.FAILED,
            "errors": ["No relevant documents found after retries"],
            "loop_count": 1
        }
    else:
        print(f"    → Sufficient docs, proceeding to generation")
        return {
            "filtered_documents": filtered,
            "relevance_score": sum(d["relevance_score"] for d in filtered) / len(filtered),
            "stage": RAGStage.GENERATION,
            "loop_count": 1
        }

def query_rewriting_node(state: ATTECHRAGState) -> dict:
    """Node 4: Query rewriting khi retrieval thất bại"""
    question = state["question"]
    retry = state.get("retry_count", 0)
    
    # Rewrite strategies
    if retry == 0:
        new_question = question + " chi tiết"
    else:
        new_question = question + " văn bản pháp luật"
    
    print(f"    Rewrote query: '{question}' → '{new_question}'")
    
    return {
        "question": new_question,
        "expanded_queries": [new_question],
        "stage": RAGStage.RETRIEVAL,
        "loop_count": 1
    }

def generation_node(state: ATTECHRAGState) -> dict:
    """Node 5: Answer generation"""
    docs = state.get("filtered_documents", [])
    question = state["question"]
    
    if not docs:
        answer = "Xin lỗi, tôi không tìm thấy tài liệu phù hợp."
        citations = []
    else:
        # Simulate LLM generation
        answer = f"Dựa trên {len(docs)} tài liệu pháp luật, câu trả lời là:\n"
        citations = [f"{d['legal_code']}: {d['title']}" for d in docs]
        
        for i, doc in enumerate(docs[:3], 1):
            answer += f"\n{i}. {doc['title']} ({doc['legal_code']})"
    
    # Simulate confidence calculation
    confidence = sum(d["relevance_score"] for d in docs) / len(docs) if docs else 0.0
    
    print(f"    Generated answer ({len(answer)} chars, confidence={confidence:.2f})")
    
    return {
        "generation": answer,
        "citations": citations,
        "confidence_score": confidence,
        "stage": RAGStage.COMPLETED
    }

# ============================================================================
# 4. MAIN EXAMPLE
# ============================================================================

def main():
    """Example usage của advanced RAG patterns"""
    
    print("\n" + "="*70)
    print("ADVANCED RAG PATTERNS FROM LANGGRAPH - EXAMPLE IMPLEMENTATION")
    print("="*70)
    
    # 1. Build graph
    print("\n1. Building RAG Graph...")
    graph = RAGGraph(max_iterations=10)
    
    # Add nodes
    graph.add_node(RAGNode(
        name="query_expansion",
        func=query_expansion_node,
        subscribes_to=[RAGStage.INIT]
    ))
    
    graph.add_node(RAGNode(
        name="retrieval",
        func=retrieval_node,
        subscribes_to=[RAGStage.RETRIEVAL]
    ))
    
    graph.add_node(RAGNode(
        name="grading",
        func=grading_node,
        subscribes_to=[RAGStage.GRADING]
    ))
    
    graph.add_node(RAGNode(
        name="query_rewriting",
        func=query_rewriting_node,
        subscribes_to=[RAGStage.REWRITING]
    ))
    
    graph.add_node(RAGNode(
        name="generation",
        func=generation_node,
        subscribes_to=[RAGStage.GENERATION]
    ))
    
    # 2. Create initial state
    print("\n2. Creating Initial State...")
    initial_state: ATTECHRAGState = {
        "question": "Điều 10 Luật Giao thông quy định gì?",
        "user_id": "user_demo",
        "session_id": "session_demo",
        "stage": RAGStage.INIT,
        "expanded_queries": [],
        "documents": [],
        "filtered_documents": [],
        "generation": "",
        "citations": [],
        "loop_count": 0,
        "max_loops": 5,
        "retry_count": 0,
        "relevance_score": None,
        "confidence_score": None,
        "hallucination_detected": False,
        "timestamp": datetime.now(),
        "processing_time": 0.0,
        "errors": []
    }
    
    # 3. Execute graph
    print("\n3. Executing Graph...")
    final_state = graph.execute(initial_state, debug=True)
    
    # 4. Display results
    print("\n4. Final Results:")
    print(f"\nQuestion: {final_state['question']}")
    print(f"Answer: {final_state['generation'][:200]}...")
    print(f"\nCitations: {len(final_state['citations'])} documents")
    for citation in final_state['citations']:
        print(f"  - {citation}")
    
    print(f"\nMetrics:")
    print(f"  - Processing time: {final_state['processing_time']:.3f}s")
    print(f"  - Loop count: {final_state['loop_count']}")
    print(f"  - Retry count: {final_state['retry_count']}")
    confidence = final_state['confidence_score']
    if confidence is not None:
        print(f"  - Confidence: {confidence:.2f}")
    else:
        print(f"  - Confidence: N/A")
    print(f"  - Errors: {len(final_state['errors'])}")
    
    if final_state['errors']:
        print(f"\nErrors encountered:")
        for error in final_state['errors']:
            print(f"  - {error}")
    
    # 5. Test state merging
    print("\n" + "="*70)
    print("5. Testing State Merge Pattern...")
    test_state: ATTECHRAGState = {
        "question": "test",
        "user_id": "u1",
        "session_id": "s1",
        "stage": RAGStage.INIT,
        "expanded_queries": ["q1"],
        "documents": [{"document_id": "d1", "legal_code": "1/2024", "title": "Doc 1", 
                      "content": "", "relevance_score": 0.8}],
        "filtered_documents": [],
        "generation": "",
        "citations": [],
        "loop_count": 1,
        "max_loops": 5,
        "retry_count": 0,
        "relevance_score": None,
        "confidence_score": None,
        "hallucination_detected": False,
        "timestamp": datetime.now(),
        "processing_time": 0.5,
        "errors": ["error1"]
    }
    
    update = {
        "documents": [{"document_id": "d2", "legal_code": "2/2024", "title": "Doc 2",
                      "content": "", "relevance_score": 0.9}],
        "loop_count": 1,
        "errors": ["error2"],
        "processing_time": 0.3
    }
    
    merged = merge_rag_state(test_state, update)
    
    print(f"Original documents: {len(test_state['documents'])}")
    print(f"After merge: {len(merged['documents'])} (auto-merged)")
    print(f"Original loop_count: {test_state['loop_count']}")
    print(f"After merge: {merged['loop_count']} (auto-incremented)")
    print(f"Original errors: {test_state['errors']}")
    print(f"After merge: {merged['errors']} (auto-merged)")
    print(f"Processing time: {test_state['processing_time']} + {update['processing_time']} = {merged['processing_time']}")
    
    print("\n" + "="*70)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
