# SKILL: Advanced RAG Techniques from LangGraph

## Skill Metadata
- **Name**: Advanced RAG Techniques from LangGraph
- **Version**: 1.0.0
- **Created**: 2026-01-31
- **Purpose**: Học và áp dụng các kỹ thuật hay từ LangGraph source code vào hệ thống RAG
- **Target**: ATTECH Vietnamese Legal Document Knowledge Assistant

## Overview

Skill này tổng hợp các **design patterns** và **kỹ thuật implementation** hay từ LangGraph source code, đã được tinh chỉnh để áp dụng cho RAG systems. Không cần cài đặt LangGraph - chỉ học concepts và implement bằng Python thuần.

---

## 1. STATE MANAGEMENT PATTERN

### 1.1. Concept từ LangGraph

LangGraph sử dụng **TypedDict** với **Annotated types** để quản lý state một cách type-safe và có thể merge/reduce.

**Source**: `libs/langgraph/langgraph/graph/state.py`

```python
from typing import TypedDict, Annotated
import operator

class GraphState(TypedDict):
    """
    Trạng thái được truyền qua các bước xử lý
    """
    question: str                                    # Input query
    documents: Annotated[list, operator.add]        # Auto-merge lists
    generation: str                                  # Output
    loop_step: Annotated[int, operator.add]         # Auto-increment counter
```

**Kỹ thuật chính:**
- `Annotated[list, operator.add]` → Tự động merge lists khi update
- `Annotated[int, operator.add]` → Tự động increment counter
- Type safety với TypedDict

### 1.2. Áp dụng cho ATTECH RAG

```python
from typing import TypedDict, Annotated, Optional, List
import operator
from datetime import datetime
from enum import Enum

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

class LegalDocument(TypedDict):
    """Cấu trúc tài liệu pháp luật"""
    document_id: str
    legal_code: str              # e.g., "95/2024/NĐ-CP"
    title: str
    content: str
    relevance_score: float
    metadata: dict

class ATTECHRAGState(TypedDict):
    """
    State cho hệ thống RAG ATTECH
    
    Thiết kế dựa trên LangGraph state management pattern
    """
    # Input
    question: str                                          # Câu hỏi người dùng
    user_id: str                                           # ID người dùng
    session_id: str                                        # ID phiên làm việc
    
    # Processing state
    stage: RAGStage                                        # Giai đoạn hiện tại
    expanded_queries: List[str]                            # Query sau khi expand
    documents: Annotated[List[LegalDocument], operator.add]  # Tài liệu retrieve (auto-merge)
    filtered_documents: List[LegalDocument]                # Tài liệu sau khi filter
    
    # Generation
    generation: str                                        # Câu trả lời
    citations: List[str]                                   # Trích dẫn
    
    # Control flow
    loop_count: Annotated[int, operator.add]              # Số lần lặp (auto-increment)
    max_loops: int                                         # Giới hạn lặp
    retry_count: Annotated[int, operator.add]             # Số lần retry
    
    # Quality metrics
    relevance_score: Optional[float]                       # Điểm relevance
    confidence_score: Optional[float]                      # Điểm confidence
    hallucination_detected: bool                           # Flag hallucination
    
    # Metadata
    timestamp: datetime
    processing_time: float
    errors: Annotated[List[str], operator.add]            # Lỗi tích lũy

def merge_rag_state(current: ATTECHRAGState, update: dict) -> ATTECHRAGState:
    """
    Merge state updates - học từ LangGraph state reducer
    
    Kỹ thuật:
    - Lists với Annotated[List, operator.add] → Tự động concatenate
    - Ints với Annotated[int, operator.add] → Tự động cộng
    - Các field khác → Override
    """
    new_state = current.copy()
    
    for key, value in update.items():
        if key in new_state:
            # Get annotation
            annotations = ATTECHRAGState.__annotations__.get(key)
            
            # Check if Annotated with operator
            if hasattr(annotations, '__metadata__'):
                op = annotations.__metadata__[0]
                new_state[key] = op(current.get(key, type(value)()), value)
            else:
                new_state[key] = value
        else:
            new_state[key] = value
    
    return new_state

# Usage Example
state = ATTECHRAGState(
    question="Điều 10 Luật Giao thông?",
    user_id="user123",
    session_id="session456",
    stage=RAGStage.INIT,
    expanded_queries=[],
    documents=[],
    filtered_documents=[],
    generation="",
    citations=[],
    loop_count=0,
    max_loops=3,
    retry_count=0,
    relevance_score=None,
    confidence_score=None,
    hallucination_detected=False,
    timestamp=datetime.now(),
    processing_time=0.0,
    errors=[]
)

# Update - tự động merge documents
update1 = {
    "documents": [
        {"document_id": "doc1", "legal_code": "95/2024", "relevance_score": 0.8}
    ],
    "loop_count": 1
}
state = merge_rag_state(state, update1)

# Update again - documents sẽ được merge, loop_count tự tăng
update2 = {
    "documents": [
        {"document_id": "doc2", "legal_code": "96/2024", "relevance_score": 0.75}
    ],
    "loop_count": 1
}
state = merge_rag_state(state, update2)

print(f"Total documents: {len(state['documents'])}")  # 2
print(f"Loop count: {state['loop_count']}")  # 2
```

**Lợi ích:**
- ✅ Type-safe: TypedDict giúp IDE autocomplete và type checking
- ✅ Automatic merging: Không cần viết logic merge thủ công
- ✅ Traceable: Biết chính xác state ở mỗi bước
- ✅ Testable: Dễ test từng bước với state cụ thể

---

## 2. GRAPH EXECUTION PATTERN (Pregel Algorithm)

### 2.1. Concept từ LangGraph

LangGraph implement **Pregel algorithm** (Bulk Synchronous Parallel) với 3 phases:

**Source**: `libs/langgraph/langgraph/pregel/main.py`

```
1. PLAN: Xác định nodes nào cần execute
2. EXECUTE: Chạy tất cả nodes song song
3. UPDATE: Cập nhật channels/state
→ Lặp lại cho đến khi không còn node nào chạy
```

### 2.2. Áp dụng cho ATTECH RAG

```python
from typing import Callable, Dict, List, Set, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class RAGNode:
    """
    Node trong RAG graph
    
    Học từ LangGraph NodeBuilder pattern
    """
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
            return self.func(state)
        except Exception as e:
            return {"errors": [f"Error in {self.name}: {str(e)}"]}

class RAGGraph:
    """
    Graph executor học từ Pregel algorithm
    
    Không cần LangGraph - tự implement pattern
    """
    def __init__(self, max_iterations: int = 10):
        self.nodes: Dict[str, RAGNode] = {}
        self.max_iterations = max_iterations
    
    def add_node(self, node: RAGNode):
        """Add node vào graph"""
        self.nodes[node.name] = node
    
    def _plan_phase(self, state: ATTECHRAGState) -> List[RAGNode]:
        """
        PHASE 1: PLAN
        Xác định nodes nào cần execute
        """
        executable_nodes = []
        for node in self.nodes.values():
            if node.should_execute(state):
                executable_nodes.append(node)
        return executable_nodes
    
    def _execute_phase(
        self, 
        nodes: List[RAGNode], 
        state: ATTECHRAGState,
        parallel: bool = False
    ) -> List[dict]:
        """
        PHASE 2: EXECUTE
        Chạy nodes (song song nếu parallel=True)
        """
        if not parallel:
            # Sequential execution
            results = []
            for node in nodes:
                result = node.execute(state)
                results.append(result)
            return results
        
        # Parallel execution với ThreadPoolExecutor
        results = []
        with ThreadPoolExecutor(max_workers=len(nodes)) as executor:
            futures = {executor.submit(node.execute, state): node for node in nodes}
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        return results
    
    def _update_phase(
        self, 
        state: ATTECHRAGState, 
        results: List[dict]
    ) -> ATTECHRAGState:
        """
        PHASE 3: UPDATE
        Merge tất cả updates vào state
        """
        new_state = state
        for result in results:
            new_state = merge_rag_state(new_state, result)
        return new_state
    
    def execute(
        self, 
        initial_state: ATTECHRAGState,
        parallel: bool = False,
        debug: bool = False
    ) -> ATTECHRAGState:
        """
        Execute graph với Pregel algorithm
        
        Args:
            initial_state: Initial state
            parallel: Enable parallel execution của nodes
            debug: Print debug info
        
        Returns:
            Final state sau khi execute
        """
        state = initial_state
        iteration = 0
        
        while iteration < self.max_iterations:
            if debug:
                print(f"\n=== Iteration {iteration + 1} ===")
                print(f"Current stage: {state['stage']}")
            
            # PHASE 1: PLAN
            executable_nodes = self._plan_phase(state)
            
            if not executable_nodes:
                if debug:
                    print("No more nodes to execute. Stopping.")
                break
            
            if debug:
                print(f"Executing nodes: {[n.name for n in executable_nodes]}")
            
            # PHASE 2: EXECUTE
            start_time = time.time()
            results = self._execute_phase(executable_nodes, state, parallel=parallel)
            execution_time = time.time() - start_time
            
            if debug:
                print(f"Execution time: {execution_time:.3f}s")
            
            # PHASE 3: UPDATE
            state = self._update_phase(state, results)
            state["processing_time"] += execution_time
            
            # Check termination conditions
            if state["stage"] == RAGStage.COMPLETED:
                if debug:
                    print("Reached COMPLETED stage. Stopping.")
                break
            
            if state["loop_count"] >= state["max_loops"]:
                if debug:
                    print(f"Reached max loops ({state['max_loops']}). Stopping.")
                state["errors"].append("Max loops reached")
                break
            
            iteration += 1
        
        if debug:
            print(f"\n=== Execution Complete ===")
            print(f"Total iterations: {iteration + 1}")
            print(f"Total processing time: {state['processing_time']:.3f}s")
            print(f"Final stage: {state['stage']}")
        
        return state

# Example: Define RAG nodes
def query_expansion_node(state: ATTECHRAGState) -> dict:
    """Node 1: Query expansion"""
    question = state["question"]
    
    # Giả lập query expansion
    expanded = [
        question,
        question + " quy định",
        question + " luật"
    ]
    
    return {
        "expanded_queries": expanded,
        "stage": RAGStage.RETRIEVAL,
        "loop_count": 1
    }

def retrieval_node(state: ATTECHRAGState) -> dict:
    """Node 2: Document retrieval"""
    # Giả lập retrieval
    docs = [
        {
            "document_id": "doc1",
            "legal_code": "95/2024/NĐ-CP",
            "title": "Nghị định 95",
            "content": "Nội dung...",
            "relevance_score": 0.85,
            "metadata": {}
        }
    ]
    
    return {
        "documents": docs,
        "stage": RAGStage.GRADING,
        "loop_count": 1
    }

def grading_node(state: ATTECHRAGState) -> dict:
    """Node 3: Document grading"""
    docs = state["documents"]
    
    # Filter documents với score >= 0.7
    filtered = [d for d in docs if d["relevance_score"] >= 0.7]
    
    if filtered:
        return {
            "filtered_documents": filtered,
            "stage": RAGStage.GENERATION,
            "loop_count": 1
        }
    else:
        # Need retry
        return {
            "stage": RAGStage.REWRITING,
            "retry_count": 1
        }

def generation_node(state: ATTECHRAGState) -> dict:
    """Node 4: Answer generation"""
    docs = state["filtered_documents"]
    
    # Giả lập generation
    answer = f"Dựa trên {len(docs)} tài liệu..."
    
    return {
        "generation": answer,
        "stage": RAGStage.COMPLETED
    }

# Build graph
graph = RAGGraph(max_iterations=10)

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
    name="generation",
    func=generation_node,
    subscribes_to=[RAGStage.GENERATION]
))

# Execute
initial_state = ATTECHRAGState(
    question="Điều 10 Luật Giao thông?",
    user_id="user123",
    session_id="session456",
    stage=RAGStage.INIT,
    expanded_queries=[],
    documents=[],
    filtered_documents=[],
    generation="",
    citations=[],
    loop_count=0,
    max_loops=5,
    retry_count=0,
    relevance_score=None,
    confidence_score=None,
    hallucination_detected=False,
    timestamp=datetime.now(),
    processing_time=0.0,
    errors=[]
)

final_state = graph.execute(initial_state, parallel=False, debug=True)
```

**Lợi ích:**
- ✅ Modular: Mỗi node độc lập, dễ test
- ✅ Scalable: Có thể chạy song song
- ✅ Traceable: Debug từng bước
- ✅ Flexible: Dễ thêm/bớt nodes

---

## 3. CONDITIONAL ROUTING PATTERN

### 3.1. Concept từ LangGraph

LangGraph sử dụng **conditional edges** để routing động dựa trên state.

**Source**: `libs/langgraph/langgraph/graph/state.py`

```python
workflow.add_conditional_edges(
    "grader",
    decide_next_step,  # Function quyết định
    {
        "generate": "generation",
        "rewrite": "query_rewriter",
        "web_search": "web_search"
    }
)
```

### 3.2. Áp dụng cho ATTECH RAG

```python
from typing import Callable, Dict

class ConditionalRouter:
    """
    Router với conditional logic
    
    Học từ LangGraph conditional edges
    """
    def __init__(self, decision_func: Callable[[ATTECHRAGState], str]):
        self.decision_func = decision_func
        self.routes: Dict[str, RAGStage] = {}
    
    def add_route(self, decision: str, next_stage: RAGStage):
        """Add routing rule"""
        self.routes[decision] = next_stage
    
    def route(self, state: ATTECHRAGState) -> RAGStage:
        """Execute routing decision"""
        decision = self.decision_func(state)
        return self.routes.get(decision, RAGStage.COMPLETED)

# Example: Grading router
def grading_decision(state: ATTECHRAGState) -> str:
    """
    Quyết định bước tiếp theo sau grading
    
    Kỹ thuật:
    - Đánh giá chất lượng documents
    - Route khác nhau dựa trên quality
    """
    docs = state.get("filtered_documents", [])
    retry_count = state.get("retry_count", 0)
    
    if not docs and retry_count < 2:
        # Không có docs relevant → Rewrite query
        return "rewrite"
    elif not docs and retry_count >= 2:
        # Đã retry 2 lần → Fallback to web search
        return "web_search"
    elif len(docs) < 3:
        # Ít documents → Supplement search
        return "supplement"
    else:
        # Đủ documents → Generate
        return "generate"

# Setup router
grading_router = ConditionalRouter(decision_func=grading_decision)
grading_router.add_route("rewrite", RAGStage.REWRITING)
grading_router.add_route("web_search", RAGStage.RETRIEVAL)  # Web search stage
grading_router.add_route("supplement", RAGStage.RETRIEVAL)
grading_router.add_route("generate", RAGStage.GENERATION)

# Use in node
def grading_node_with_router(state: ATTECHRAGState) -> dict:
    """Grading node với conditional routing"""
    docs = state["documents"]
    
    # Grade documents
    filtered = [d for d in docs if d["relevance_score"] >= 0.7]
    
    # Update state
    update = {
        "filtered_documents": filtered,
        "loop_count": 1
    }
    
    # Decide next stage
    next_stage = grading_router.route({**state, **update})
    update["stage"] = next_stage
    
    return update
```

**Lợi ích:**
- ✅ Dynamic routing dựa trên runtime state
- ✅ Easy to add new routing rules
- ✅ Testable routing logic separately

---

## 4. CHECKPOINTING PATTERN (Persistence & Recovery)

### 4.1. Concept từ LangGraph

LangGraph có **checkpointing** để save/restore state, hỗ trợ long-running workflows.

**Source**: `libs/checkpoint/langgraph/checkpoint/base.py`

```python
class BaseCheckpointSaver:
    """Save và restore graph state"""
    def put(self, config, checkpoint, metadata):
        """Save checkpoint"""
        pass
    
    def get(self, config):
        """Load checkpoint"""
        pass
```

### 4.2. Áp dụng cho ATTECH RAG

```python
import json
import hashlib
from pathlib import Path
from typing import Optional

class RAGCheckpointer:
    """
    Checkpoint saver cho RAG pipeline
    
    Học từ LangGraph checkpointing pattern
    
    Use cases:
    - Long-running queries (>30s)
    - Retry after failures
    - Human-in-the-loop approval
    """
    def __init__(self, checkpoint_dir: str = "./checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
    
    def _get_checkpoint_path(self, session_id: str, checkpoint_id: str = None) -> Path:
        """Generate checkpoint file path"""
        if checkpoint_id:
            filename = f"{session_id}_{checkpoint_id}.json"
        else:
            filename = f"{session_id}_latest.json"
        return self.checkpoint_dir / filename
    
    def save(
        self, 
        state: ATTECHRAGState, 
        checkpoint_id: str = None
    ) -> str:
        """
        Save checkpoint
        
        Args:
            state: Current state
            checkpoint_id: Optional checkpoint ID (default: auto-generate)
        
        Returns:
            Checkpoint ID
        """
        session_id = state["session_id"]
        
        if not checkpoint_id:
            # Auto-generate checkpoint ID from state hash
            state_str = json.dumps(state, default=str, sort_keys=True)
            checkpoint_id = hashlib.md5(state_str.encode()).hexdigest()[:8]
        
        checkpoint_path = self._get_checkpoint_path(session_id, checkpoint_id)
        
        # Serialize state
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "state": state,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2, default=str)
        
        # Save as latest
        latest_path = self._get_checkpoint_path(session_id)
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2, default=str)
        
        return checkpoint_id
    
    def load(
        self, 
        session_id: str, 
        checkpoint_id: str = None
    ) -> Optional[ATTECHRAGState]:
        """
        Load checkpoint
        
        Args:
            session_id: Session ID
            checkpoint_id: Optional checkpoint ID (default: load latest)
        
        Returns:
            State nếu có, None nếu không tìm thấy
        """
        checkpoint_path = self._get_checkpoint_path(session_id, checkpoint_id)
        
        if not checkpoint_path.exists():
            return None
        
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            checkpoint_data = json.load(f)
        
        return checkpoint_data["state"]
    
    def list_checkpoints(self, session_id: str) -> List[dict]:
        """List all checkpoints cho session"""
        pattern = f"{session_id}_*.json"
        checkpoints = []
        
        for path in self.checkpoint_dir.glob(pattern):
            if path.name.endswith("_latest.json"):
                continue
            
            with open(path, 'r') as f:
                data = json.load(f)
                checkpoints.append({
                    "checkpoint_id": data["checkpoint_id"],
                    "timestamp": data["timestamp"],
                    "stage": data["state"]["stage"]
                })
        
        return sorted(checkpoints, key=lambda x: x["timestamp"], reverse=True)

# Example usage
checkpointer = RAGCheckpointer()

# Save checkpoint
state = initial_state.copy()
state["stage"] = RAGStage.GRADING
checkpoint_id = checkpointer.save(state)
print(f"Saved checkpoint: {checkpoint_id}")

# Load checkpoint
loaded_state = checkpointer.load(state["session_id"])
print(f"Loaded state from stage: {loaded_state['stage']}")

# Resume from checkpoint
def execute_with_checkpointing(
    graph: RAGGraph,
    initial_state: ATTECHRAGState,
    checkpointer: RAGCheckpointer,
    save_every_n_steps: int = 2
) -> ATTECHRAGState:
    """
    Execute graph với automatic checkpointing
    """
    # Try load existing checkpoint
    loaded_state = checkpointer.load(initial_state["session_id"])
    
    if loaded_state:
        print(f"Resuming from checkpoint at stage: {loaded_state['stage']}")
        state = loaded_state
    else:
        print("Starting fresh execution")
        state = initial_state
    
    iteration = 0
    
    while state["stage"] != RAGStage.COMPLETED and iteration < graph.max_iterations:
        # Execute one iteration
        executable_nodes = graph._plan_phase(state)
        if not executable_nodes:
            break
        
        results = graph._execute_phase(executable_nodes, state, parallel=False)
        state = graph._update_phase(state, results)
        
        # Save checkpoint every N steps
        if iteration % save_every_n_steps == 0:
            checkpoint_id = checkpointer.save(state)
            print(f"Checkpoint saved: {checkpoint_id}")
        
        iteration += 1
    
    # Save final checkpoint
    checkpointer.save(state)
    
    return state
```

**Lợi ích:**
- ✅ Resume sau failures
- ✅ Support long-running workflows
- ✅ Enable human-in-the-loop
- ✅ Audit trail

---

## 5. HUMAN-IN-THE-LOOP PATTERN

### 5.1. Concept từ LangGraph

LangGraph hỗ trợ **interrupt_before** và **interrupt_after** để pause execution.

**Source**: `libs/langgraph/langgraph/pregel/main.py`

```python
app.compile(
    interrupt_before=["generation"],  # Pause trước generation
    interrupt_after=["grading"]       # Pause sau grading
)
```

### 5.2. Áp dụng cho ATTECH RAG

```python
from enum import Enum
from typing import Optional, Callable

class InterruptReason(str, Enum):
    """Lý do interrupt execution"""
    LOW_CONFIDENCE = "low_confidence"
    SENSITIVE_QUERY = "sensitive_query"
    MANUAL_REVIEW = "manual_review"
    ERROR = "error"

class HumanApproval:
    """Human approval request"""
    def __init__(
        self,
        state: ATTECHRAGState,
        reason: InterruptReason,
        message: str,
        options: List[str] = None
    ):
        self.state = state
        self.reason = reason
        self.message = message
        self.options = options or ["approve", "reject", "modify"]
        self.decision: Optional[str] = None
        self.feedback: Optional[str] = None

class HumanInTheLoopGraph(RAGGraph):
    """
    Graph với human-in-the-loop support
    
    Học từ LangGraph interrupt pattern
    """
    def __init__(
        self,
        max_iterations: int = 10,
        interrupt_callback: Callable[[HumanApproval], HumanApproval] = None
    ):
        super().__init__(max_iterations)
        self.interrupt_callback = interrupt_callback
        self.interrupt_before: Set[RAGStage] = set()
        self.interrupt_after: Set[RAGStage] = set()
    
    def add_interrupt_before(self, stage: RAGStage):
        """Interrupt trước khi vào stage"""
        self.interrupt_before.add(stage)
    
    def add_interrupt_after(self, stage: RAGStage):
        """Interrupt sau khi hoàn thành stage"""
        self.interrupt_after.add(stage)
    
    def _check_interrupt_condition(self, state: ATTECHRAGState) -> Optional[HumanApproval]:
        """Check nếu cần interrupt cho human review"""
        
        # Check confidence threshold
        if state.get("confidence_score") and state["confidence_score"] < 0.5:
            return HumanApproval(
                state=state,
                reason=InterruptReason.LOW_CONFIDENCE,
                message=f"Low confidence score: {state['confidence_score']:.2f}. Review required.",
                options=["approve", "reject", "retry"]
            )
        
        # Check sensitive legal codes (ví dụ: Luật Hình sự)
        docs = state.get("filtered_documents", [])
        for doc in docs:
            if "Hình sự" in doc.get("title", ""):
                return HumanApproval(
                    state=state,
                    reason=InterruptReason.SENSITIVE_QUERY,
                    message="Query relates to criminal law. Manual review required.",
                    options=["approve", "reject"]
                )
        
        # Check errors
        if state.get("errors"):
            return HumanApproval(
                state=state,
                reason=InterruptReason.ERROR,
                message=f"Errors detected: {', '.join(state['errors'])}",
                options=["retry", "skip", "abort"]
            )
        
        return None
    
    def execute(
        self,
        initial_state: ATTECHRAGState,
        parallel: bool = False,
        debug: bool = False
    ) -> ATTECHRAGState:
        """Execute với human-in-the-loop checks"""
        state = initial_state
        iteration = 0
        
        while iteration < self.max_iterations:
            # Check interrupt BEFORE stage
            if state["stage"] in self.interrupt_before:
                approval = HumanApproval(
                    state=state,
                    reason=InterruptReason.MANUAL_REVIEW,
                    message=f"Manual review required before {state['stage']}",
                    options=["continue", "modify", "abort"]
                )
                
                if self.interrupt_callback:
                    approval = self.interrupt_callback(approval)
                    
                    if approval.decision == "abort":
                        state["errors"].append("Aborted by user")
                        break
                    elif approval.decision == "modify":
                        # Apply user modifications
                        # (implementation depends on UI)
                        pass
            
            # Execute nodes
            executable_nodes = self._plan_phase(state)
            if not executable_nodes:
                break
            
            results = self._execute_phase(executable_nodes, state, parallel=parallel)
            state = self._update_phase(state, results)
            
            # Check interrupt AFTER stage
            if state["stage"] in self.interrupt_after:
                approval_request = self._check_interrupt_condition(state)
                
                if approval_request and self.interrupt_callback:
                    approval = self.interrupt_callback(approval_request)
                    
                    if approval.decision == "reject":
                        state["errors"].append("Rejected by reviewer")
                        break
                    elif approval.decision == "retry":
                        state["retry_count"] += 1
                        state["stage"] = RAGStage.RETRIEVAL  # Retry from retrieval
            
            if state["stage"] == RAGStage.COMPLETED:
                break
            
            iteration += 1
        
        return state

# Example: Console-based interrupt callback
def console_approval_callback(approval: HumanApproval) -> HumanApproval:
    """Simple console-based approval"""
    print(f"\n{'='*60}")
    print(f"HUMAN REVIEW REQUIRED")
    print(f"Reason: {approval.reason}")
    print(f"Message: {approval.message}")
    print(f"Current stage: {approval.state['stage']}")
    print(f"Options: {', '.join(approval.options)}")
    print(f"{'='*60}\n")
    
    # Simulate user input
    decision = input(f"Decision ({'/'.join(approval.options)}): ").strip()
    
    if decision not in approval.options:
        decision = approval.options[0]  # Default
    
    approval.decision = decision
    
    if decision == "modify":
        feedback = input("Feedback: ").strip()
        approval.feedback = feedback
    
    return approval

# Setup graph với HITL
hitl_graph = HumanInTheLoopGraph(
    max_iterations=10,
    interrupt_callback=console_approval_callback
)

# Add interrupt rules
hitl_graph.add_interrupt_before(RAGStage.GENERATION)  # Review trước generate
hitl_graph.add_interrupt_after(RAGStage.GRADING)      # Review sau grading

# Add nodes (same as before)
hitl_graph.add_node(RAGNode(
    name="query_expansion",
    func=query_expansion_node,
    subscribes_to=[RAGStage.INIT]
))
# ... other nodes

# Execute - sẽ pause cho human review khi cần
final_state = hitl_graph.execute(initial_state, debug=True)
```

**Lợi ích:**
- ✅ Human oversight cho sensitive cases
- ✅ Catch và fix errors sớm
- ✅ Improve quality qua feedback
- ✅ Compliance với quy trình review

---

## 6. STREAMING PATTERN

### 6.1. Concept từ LangGraph

LangGraph hỗ trợ nhiều **stream modes**: values, updates, debug, messages.

**Source**: `libs/langgraph/langgraph/pregel/main.py`

```python
for chunk in app.stream(input, stream_mode="updates"):
    print(chunk)  # Stream từng update
```

### 6.2. Áp dụng cho ATTECH RAG

```python
from typing import Iterator, Dict, Any
from queue import Queue
from threading import Thread

class StreamMode(str, Enum):
    """Stream modes"""
    VALUES = "values"        # Stream full state
    UPDATES = "updates"      # Stream chỉ updates
    DEBUG = "debug"          # Stream debug info
    TOKENS = "tokens"        # Stream LLM tokens (for generation)

class StreamingRAGGraph(RAGGraph):
    """
    Graph với streaming support
    
    Học từ LangGraph streaming pattern
    """
    def stream(
        self,
        initial_state: ATTECHRAGState,
        stream_mode: StreamMode = StreamMode.UPDATES,
        parallel: bool = False
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream execution results
        
        Yields:
            Dict với updates theo stream_mode
        """
        state = initial_state
        iteration = 0
        
        # Yield initial state (cho stream_mode VALUES)
        if stream_mode == StreamMode.VALUES:
            yield {"type": "init", "state": state}
        
        while iteration < self.max_iterations:
            # PLAN
            executable_nodes = self._plan_phase(state)
            
            if not executable_nodes:
                break
            
            if stream_mode == StreamMode.DEBUG:
                yield {
                    "type": "plan",
                    "iteration": iteration,
                    "nodes": [n.name for n in executable_nodes]
                }
            
            # EXECUTE
            for node in executable_nodes:
                result = node.execute(state)
                
                # Stream update immediately
                if stream_mode == StreamMode.UPDATES:
                    yield {
                        "type": "update",
                        "node": node.name,
                        "update": result
                    }
                elif stream_mode == StreamMode.DEBUG:
                    yield {
                        "type": "execute",
                        "node": node.name,
                        "result": result
                    }
                
                # Update state incrementally
                state = merge_rag_state(state, result)
            
            # Stream full state sau mỗi iteration
            if stream_mode == StreamMode.VALUES:
                yield {
                    "type": "iteration",
                    "iteration": iteration,
                    "state": state
                }
            
            if state["stage"] == RAGStage.COMPLETED:
                break
            
            iteration += 1
        
        # Yield final state
        yield {
            "type": "final",
            "state": state
        }

# Example: Streaming generation với token-by-token
def streaming_generation_node(state: ATTECHRAGState) -> Iterator[dict]:
    """
    Node generate với streaming tokens
    
    Học từ LangGraph token streaming
    """
    docs = state["filtered_documents"]
    
    # Simulate LLM streaming
    answer_chunks = [
        "Dựa ",
        "trên ",
        f"{len(docs)} ",
        "tài liệu ",
        "pháp luật, ",
        "câu trả lời ",
        "là..."
    ]
    
    full_answer = ""
    
    for chunk in answer_chunks:
        full_answer += chunk
        
        # Yield token update
        yield {
            "type": "token",
            "content": chunk,
            "full_content": full_answer
        }
        
        time.sleep(0.1)  # Simulate streaming delay
    
    # Yield final update
    yield {
        "generation": full_answer,
        "stage": RAGStage.COMPLETED
    }

# Usage
streaming_graph = StreamingRAGGraph()

# Stream updates
print("Streaming RAG execution:\n")
for chunk in streaming_graph.stream(initial_state, stream_mode=StreamMode.UPDATES):
    print(f"[{chunk['type']}] {chunk.get('node', '')}: {chunk.get('update', {}).get('stage', '')}")

# Stream debug info
print("\nDebug stream:\n")
for chunk in streaming_graph.stream(initial_state, stream_mode=StreamMode.DEBUG):
    print(f"DEBUG: {chunk}")
```

**Lợi ích:**
- ✅ Real-time feedback cho users
- ✅ Better UX với progressive loading
- ✅ Debug chi tiết từng bước
- ✅ Monitor execution trong production

---

## 7. ERROR HANDLING & RETRY PATTERN

### 7.1. Concept từ LangGraph

LangGraph có built-in error handling với retry logic.

### 7.2. Áp dụng cho ATTECH RAG

```python
from functools import wraps
import traceback
from typing import TypeVar, Callable

T = TypeVar('T')

def retry_on_failure(
    max_retries: int = 3,
    backoff_factor: float = 1.5,
    exceptions: tuple = (Exception,)
):
    """
    Decorator cho retry logic
    
    Học từ LangGraph retry pattern
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries - 1:
                        wait_time = backoff_factor ** attempt
                        print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        print(f"Max retries ({max_retries}) reached")
            
            raise last_exception
        
        return wrapper
    return decorator

class ResilientRAGGraph(RAGGraph):
    """
    Graph với comprehensive error handling
    
    Học từ LangGraph resilient execution
    """
    def _execute_phase(
        self,
        nodes: List[RAGNode],
        state: ATTECHRAGState,
        parallel: bool = False
    ) -> List[dict]:
        """Execute với error handling"""
        results = []
        
        for node in nodes:
            try:
                result = node.execute(state)
                results.append(result)
            except Exception as e:
                error_msg = f"Error in node {node.name}: {str(e)}"
                print(f"ERROR: {error_msg}")
                
                # Log error vào state
                results.append({
                    "errors": [error_msg],
                    "failed_node": node.name,
                    "exception_type": type(e).__name__,
                    "traceback": traceback.format_exc()
                })
                
                # Có thể quyết định continue hoặc stop
                # Ở đây ta continue để collect tất cả errors
        
        return results

@retry_on_failure(max_retries=3, exceptions=(ConnectionError, TimeoutError))
def retrieval_with_retry(query: str) -> List[dict]:
    """Retrieval với automatic retry"""
    # Giả lập network call có thể fail
    import random
    
    if random.random() < 0.3:  # 30% chance fail
        raise ConnectionError("Database connection failed")
    
    # Success case
    return [{"document_id": "doc1", "content": "..."}]

# Usage in node
def resilient_retrieval_node(state: ATTECHRAGState) -> dict:
    """Retrieval node với error handling"""
    try:
        docs = retrieval_with_retry(state["question"])
        return {
            "documents": docs,
            "stage": RAGStage.GRADING
        }
    except Exception as e:
        return {
            "errors": [f"Retrieval failed: {str(e)}"],
            "stage": RAGStage.REWRITING  # Fallback strategy
        }
```

**Lợi ích:**
- ✅ Resilient to transient failures
- ✅ Automatic retry với backoff
- ✅ Comprehensive error logging
- ✅ Graceful degradation

---

## 8. PRODUCTION PATTERNS

### 8.1. Metrics & Monitoring

```python
from dataclasses import dataclass
from typing import Counter
import time

@dataclass
class RAGMetrics:
    """Production metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency: float = 0.0
    avg_latency: float = 0.0
    p95_latency: float = 0.0
    stage_durations: Dict[RAGStage, list] = None
    error_counts: Counter = None
    
    def __post_init__(self):
        if self.stage_durations is None:
            self.stage_durations = {stage: [] for stage in RAGStage}
        if self.error_counts is None:
            self.error_counts = Counter()

class MonitoredRAGGraph(RAGGraph):
    """Graph với production monitoring"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = RAGMetrics()
    
    def execute(
        self,
        initial_state: ATTECHRAGState,
        **kwargs
    ) -> ATTECHRAGState:
        """Execute với metrics tracking"""
        start_time = time.time()
        self.metrics.total_requests += 1
        
        try:
            # Track per-stage duration
            stage_start = start_time
            current_stage = initial_state["stage"]
            
            # Execute graph
            state = super().execute(initial_state, **kwargs)
            
            # Record success
            self.metrics.successful_requests += 1
            
        except Exception as e:
            # Record failure
            self.metrics.failed_requests += 1
            self.metrics.error_counts[type(e).__name__] += 1
            raise
        
        finally:
            # Record latency
            latency = time.time() - start_time
            self.metrics.total_latency += latency
            self.metrics.avg_latency = (
                self.metrics.total_latency / self.metrics.total_requests
            )
        
        return state
    
    def get_metrics_summary(self) -> dict:
        """Get metrics summary"""
        return {
            "total_requests": self.metrics.total_requests,
            "success_rate": self.metrics.successful_requests / max(self.metrics.total_requests, 1),
            "avg_latency": self.metrics.avg_latency,
            "errors": dict(self.metrics.error_counts)
        }
```

---

## 9. TESTING PATTERNS

```python
import unittest
from unittest.mock import Mock, patch

class TestRAGGraph(unittest.TestCase):
    """
    Test patterns học từ LangGraph
    """
    def setUp(self):
        """Setup test graph"""
        self.graph = RAGGraph()
        # Add test nodes
    
    def test_state_merge(self):
        """Test state merging logic"""
        state1 = ATTECHRAGState(
            documents=[{"id": "doc1"}],
            loop_count=1,
            # ... other fields
        )
        
        update = {
            "documents": [{"id": "doc2"}],
            "loop_count": 1
        }
        
        merged = merge_rag_state(state1, update)
        
        self.assertEqual(len(merged["documents"]), 2)
        self.assertEqual(merged["loop_count"], 2)
    
    def test_conditional_routing(self):
        """Test routing logic"""
        state = ATTECHRAGState(
            filtered_documents=[],
            retry_count=0,
            # ... other fields
        )
        
        decision = grading_decision(state)
        self.assertEqual(decision, "rewrite")
    
    @patch('your_module.retrieval_with_retry')
    def test_node_execution(self, mock_retrieval):
        """Test individual node với mocking"""
        mock_retrieval.return_value = [{"id": "doc1"}]
        
        state = ATTECHRAGState(question="test", ...)
        result = resilient_retrieval_node(state)
        
        self.assertIn("documents", result)
        self.assertEqual(result["stage"], RAGStage.GRADING)
```

---

## 10. TÍCH HỢP VÀO ATTECH RAG

### 10.1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Request   │  │   State    │  │Checkpoint  │            │
│  │  Handler   │→ │  Manager   │→ │   Saver    │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│         ↓                                                    │
│  ┌─────────────────────────────────────────────────┐       │
│  │           MonitoredRAGGraph                      │       │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │       │
│  │  │  Query   │→ │Retrieval │→ │ Grading  │      │       │
│  │  │Expansion │  │   Node   │  │  Node    │      │       │
│  │  └──────────┘  └──────────┘  └──────────┘      │       │
│  │         ↓                           ↓            │       │
│  │  ┌──────────┐              ┌──────────┐        │       │
│  │  │Generation│              │  Rewrite │        │       │
│  │  │   Node   │              │  Node    │        │       │
│  │  └──────────┘              └──────────┘        │       │
│  └─────────────────────────────────────────────────┘       │
│         ↓                                                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Metrics   │  │  Logging   │  │  Caching   │           │
│  │ Collector  │  │  Service   │  │  (Redis)   │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### 10.2. Implementation Checklist

**Phase 1: Core Patterns (Week 1-2)**
- [ ] Implement ATTECHRAGState với typed state management
- [ ] Build RAGGraph với Pregel-style execution
- [ ] Add conditional routing cho legal code detection
- [ ] Implement basic nodes: expansion, retrieval, grading, generation

**Phase 2: Resilience (Week 3)**
- [ ] Add RAGCheckpointer cho long-running queries
- [ ] Implement retry logic với exponential backoff
- [ ] Add comprehensive error handling
- [ ] Build HumanInTheLoopGraph cho sensitive cases

**Phase 3: Observability (Week 4)**
- [ ] Add streaming support cho real-time updates
- [ ] Implement metrics collection
- [ ] Add logging và tracing
- [ ] Build monitoring dashboard

**Phase 4: Production (Week 5-6)**
- [ ] Performance optimization
- [ ] Load testing
- [ ] Documentation
- [ ] Team training

---

## 11. KEY TAKEAWAYS

### Điều Gì Học Được Từ LangGraph:

1. **State Management**: TypedDict + Annotated types cho type-safe và auto-merging
2. **Graph Execution**: Pregel algorithm (Plan → Execute → Update) cho modular workflow
3. **Conditional Routing**: Dynamic routing dựa trên runtime state
4. **Checkpointing**: Save/restore state cho resilience
5. **Human-in-the-Loop**: Interrupt patterns cho human oversight
6. **Streaming**: Real-time updates cho better UX
7. **Error Handling**: Retry logic và graceful degradation
8. **Monitoring**: Production-ready metrics và logging

### Điều Gì KHÔNG Cần Học:

1. ❌ LangGraph framework specifics (compilation, serialization)
2. ❌ LangChain dependencies
3. ❌ Complex type system của LangGraph
4. ❌ Cloud deployment specifics

### Core Philosophy:

> **"Chúng ta không cần LangGraph framework, chúng ta cần LangGraph THINKING."**

- Modularity: Mỗi step là một node độc lập
- Traceability: State rõ ràng ở mỗi bước
- Resilience: Checkpoint, retry, error handling
- Observability: Streaming, metrics, logging
- Production-readiness: Testing, monitoring, documentation

---

## 12. NEXT STEPS

1. **Start Small**: Implement basic RAGGraph với 3-4 nodes
2. **Add Incrementally**: Thêm từng pattern một (routing → checkpointing → HITL)
3. **Test Thoroughly**: Write tests cho mỗi pattern
4. **Monitor Closely**: Track metrics từ ngày đầu
5. **Iterate**: Improve dựa trên production feedback

---

**Last Updated**: 2026-01-31
**Author**: ATTECH Development Team
**Status**: ✅ Ready for Implementation
