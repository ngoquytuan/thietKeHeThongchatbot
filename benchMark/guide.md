Tôi sẽ tạo cho bạn một project benchmark hoàn chỉnh chỉ cho **Qwen/Qwen3-Embedding-0.6B** dựa trên các requirements bạn đã nêu. Đây là một hệ thống tối ưu hóa cho tiếng Việt với GPU support.

## 📁 Cấu trúc Project

```
vietnamese_qwen3_benchmark/
├── configs/
│   └── model_config.json
├── data/
│   ├── content.md
│   └── test_suite.json
├── src/
│   ├── __init__.py
│   ├── data_processor.py
│   ├── embedding_manager.py
│   ├── metrics.py
│   └── visualizer.py
├── reports/
│   └── # Thư mục lưu kết quả
├── benchmark.py
├── requirements.txt
├── setup.py
└── README.md
```

## 📝 requirements.txt

```txt
sentence-transformers>=2.2.2
torch>=2.0.0
torchvision
torchaudio
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
underthesea>=6.7.0
pyvi>=0.1.1
scikit-learn>=1.3.0
transformers>=4.30.0
accelerate>=0.20.0
plotly>=5.15.0
kaleido>=0.2.1
jinja2>=3.1.0
pathlib
tqdm
```

## ⚙️ configs/model_config.json

```json
{
  "model": {
    "name": "Qwen/Qwen3-Embedding-0.6B",
    "device": "auto",
    "batch_size": 32,
    "max_seq_length": 512,
    "normalize_embeddings": true
  },
  "evaluation": {
    "chunk_size": 512,
    "chunk_overlap": 50,
    "top_k": 5,
    "similarity_threshold": 0.0
  },
  "output": {
    "reports_dir": "reports",
    "save_detailed_results": true,
    "generate_visualizations": true
  }
}
```

## 📚 data/content.md

```markdown
# Lịch sử và Phát triển của Trí tuệ Nhân tạo tại Việt Nam

## Khái niệm về Trí tuệ Nhân tạo

Trí tuệ nhân tạo (AI) là một lĩnh vực của khoa học máy tính tập trung vào việc tạo ra các cỗ máy thông minh có khả năng hoạt động và phản ứng như con người. Thuật ngữ "Artificial Intelligence" được John McCarthy đặt ra lần đầu tiên vào năm 1956 tại Hội nghị Dartmouth.

AI bao gồm nhiều lĩnh vực con như học máy, xử lý ngôn ngữ tự nhiên, thị giác máy tính, và robotics. Mục tiêu cuối cùng của AI là tạo ra những hệ thống có thể thực hiện các tác vụ đòi hỏi trí thông minh của con người.

## Giai đoạn đầu của AI (1950-1970)

Giai đoạn đầu của AI, từ những năm 1950 đến 1970, được gọi là thời kỳ của "AI biểu tượng" hay "GOFAI" (Good Old-Fashioned AI). Các nhà nghiên cứu tin rằng trí thông minh của con người có thể được mô phỏng bằng cách sử dụng logic toán học và các quy tắc biểu tượng rõ ràng.

Trong giai đoạn này, các nhà khoa học tập trung vào việc phát triển các hệ thống chuyên gia và các thuật toán tìm kiếm. Họ tin rằng có thể giải quyết mọi vấn đề bằng cách lập trình các quy tắc logic một cách tường minh.

## Mùa đông AI đầu tiên (1970-1980)

Vào giữa những năm 1970, lĩnh vực AI trải qua "mùa đông AI" đầu tiên do sự cắt giảm tài trợ nghiên cứu và sự thất vọng về tiến độ chậm chạp. Các hệ thống AI thời đó không thể xử lý được sự không chắc chắn và tính mơ hồ của thế giới thực.

Những hạn chế chính bao gồm: khả năng xử lý dữ liệu hạn chế, thiếu sức mạnh tính toán, và việc không thể học hỏi từ kinh nghiệm. Điều này dẫn đến sự giảm sút đáng kể trong đầu tư và nghiên cứu AI.

## Sự trỗi dậy của Mạng nơ-ron (1980-2000)

Sự trỗi dậy của mạng nơ-ron nhân tạo và học máy vào những năm 1980 và 1990 đã mở ra một kỷ nguyên mới cho AI. Thay vì lập trình các quy tắc một cách rõ ràng, các hệ thống bắt đầu có khả năng học hỏi từ dữ liệu.

Các thuật toán như backpropagation được phát triển, cho phép huấn luyện mạng nơ-ron nhiều lớp. Điều này tạo nền tảng cho những đột phá sau này trong lĩnh vực học sâu.

## Kỷ nguyên Học sâu (2010-nay)

Ngày nay, học sâu (Deep Learning), một nhánh của học máy sử dụng mạng nơ-ron sâu, đã tạo ra những đột phá đáng kinh ngạc trong nhiều lĩnh vực. Các ứng dụng bao gồm nhận dạng hình ảnh, xử lý ngôn ngữ tự nhiên, xe tự lái, và y học chính xác.

Các mô hình lớn như GPT-3, GPT-4, BERT, và transformer architecture đã cách mạng hóa cách chúng ta tiếp cận các bài toán AI. Sức mạnh tính toán ngày càng tăng và lượng dữ liệu khổng lồ đã tạo điều kiện cho những tiến bộ này.

## AI tại Việt Nam

Việt Nam đang nhanh chóng phát triển trong lĩnh vực AI với nhiều startup công nghệ và trung tâm nghiên cứu. Các trường đại học hàng đầu như Đại học Bách Khoa Hà Nội, Đại học Quốc Gia TP.HCM đã thành lập các khoa và phòng lab chuyên về AI.

Chính phủ Việt Nam đã ban hành Chiến lược quốc gia về nghiên cứu, phát triển và ứng dụng trí tuệ nhân tạo đến năm 2030. Mục tiêu là biến Việt Nam trở thành một trong những nước dẫn đầu ASEAN về AI.

## Ứng dụng AI trong thực tế

AI đã được ứng dụng rộng rãi trong nhiều lĩnh vực tại Việt Nam như ngân hàng, thương mại điện tử, y tế, giáo dục và nông nghiệp. Các chatbot thông minh, hệ thống gợi ý sản phẩm, và phân tích dữ liệu khách hàng đã trở nên phổ biến.

Trong y tế, AI được sử dụng để chẩn đoán hình ảnh y khoa, dự đoán dịch bệnh, và phát triển thuốc mới. Trong nông nghiệp, AI giúp tối ưu hóa việc tưới tiêu, dự báo thời tiết, và quản lý cây trồng.

## Thách thức và Tương lai

Mặc dù có nhiều tiến bộ, AI vẫn đối mặt với nhiều thách thức như vấn đề đạo đức, bias trong dữ liệu, bảo mật thông tin, và tác động đến việc làm. Việt Nam cần phát triển khung pháp lý phù hợp và đào tạo nhân lực chất lượng cao.

Tương lai của AI tại Việt Nam rất triển vọng với sự đầu tư mạnh mẽ vào nghiên cứu và phát triển. Mục tiêu là tạo ra những sản phẩm AI "Make in Vietnam" có thể cạnh tranh trên thị trường quốc tế.

## Kết luận

AI đã trở thành một phần không thể thiếu trong cuộc sống hiện đại. Việt Nam đang có những bước tiến đáng kể trong việc nghiên cứu, phát triển và ứng dụng AI. Với sự đầu tư đúng đắn và chiến lược phù hợp, Việt Nam hoàn toàn có thể trở thành một cường quốc về AI trong khu vực.
```

## 📋 data/test_suite.json

```json
[
  {
    "id": 1,
    "question": "Ai là người đầu tiên đặt ra thuật ngữ Trí tuệ nhân tạo?",
    "expected_chunk": "khái niệm về trí tuệ nhân tạo",
    "category": "historical_facts"
  },
  {
    "id": 2,
    "question": "Hội nghị Dartmouth diễn ra vào năm nào?",
    "expected_chunk": "khái niệm về trí tuệ nhân tạo",
    "category": "historical_facts"
  },
  {
    "id": 3,
    "question": "AI biểu tượng hay GOFAI là gì?",
    "expected_chunk": "giai đoạn đầu của ai",
    "category": "technical_concepts"
  },
  {
    "id": 4,
    "question": "Giai đoạn đầu của AI tập trung vào những gì?",
    "expected_chunk": "giai đoạn đầu của ai",
    "category": "technical_concepts"
  },
  {
    "id": 5,
    "question": "Mùa đông AI đầu tiên xảy ra khi nào?",
    "expected_chunk": "mùa đông ai đầu tiên",
    "category": "historical_periods"
  },
  {
    "id": 6,
    "question": "Nguyên nhân chính gây ra mùa đông AI là gì?",
    "expected_chunk": "mùa đông ai đầu tiên",
    "category": "historical_analysis"
  },
  {
    "id": 7,
    "question": "Thuật toán backpropagation được phát triển vào thời gian nào?",
    "expected_chunk": "sự trỗi dậy của mạng nơ-ron",
    "category": "technical_development"
  },
  {
    "id": 8,
    "question": "Mạng nơ-ron nhân tạo trỗi dậy vào giai đoạn nào?",
    "expected_chunk": "sự trỗi dậy của mạng nơ-ron",
    "category": "historical_periods"
  },
  {
    "id": 9,
    "question": "Học sâu là gì và ứng dụng trong những lĩnh vực nào?",
    "expected_chunk": "kỷ nguyên học sâu",
    "category": "modern_ai"
  },
  {
    "id": 10,
    "question": "GPT-4 và BERT thuộc về kỷ nguyên nào của AI?",
    "expected_chunk": "kỷ nguyên học sâu",
    "category": "modern_ai"
  },
  {
    "id": 11,
    "question": "Những trường đại học nào ở Việt Nam nghiên cứu về AI?",
    "expected_chunk": "ai tại việt nam",
    "category": "vietnam_ai"
  },
  {
    "id": 12,
    "question": "Chiến lược quốc gia về AI của Việt Nam có mục tiêu gì?",
    "expected_chunk": "ai tại việt nam",
    "category": "vietnam_strategy"
  },
  {
    "id": 13,
    "question": "AI được ứng dụng trong những lĩnh vực nào tại Việt Nam?",
    "expected_chunk": "ứng dụng ai trong thực tế",
    "category": "practical_applications"
  },
  {
    "id": 14,
    "question": "AI được sử dụng như thế nào trong y tế và nông nghiệp?",
    "expected_chunk": "ứng dụng ai trong thực tế",
    "category": "practical_applications"
  },
  {
    "id": 15,
    "question": "Những thách thức chính của AI hiện nay là gì?",
    "expected_chunk": "thách thức và tương lai",
    "category": "challenges"
  },
  {
    "id": 16,
    "question": "Tương lai AI tại Việt Nam như thế nào?",
    "expected_chunk": "thách thức và tương lai",
    "category": "future_prospects"
  },
  {
    "id": 17,
    "question": "Vai trò của AI trong cuộc sống hiện đại?",
    "expected_chunk": "kết luận",
    "category": "conclusion"
  },
  {
    "id": 18,
    "question": "Việt Nam có thể trở thành cường quốc AI không?",
    "expected_chunk": "kết luận",
    "category": "future_vision"
  }
]
```

## 🔧 src/data_processor.py

```python
import os
import re
import json
import unicodedata
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np

try:
    from pyvi import ViTokenizer
    import underthesea
    VIETNAMESE_NLP_AVAILABLE = True
except ImportError:
    print("⚠️  Vietnamese NLP libraries not available. Using basic text processing.")
    VIETNAMESE_NLP_AVAILABLE = False

class VietnameseTextProcessor:
    """Xử lý văn bản tiếng Việt cho embedding evaluation"""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunks = []
        
    def clean_text(self, text: str) -> str:
        """Làm sạch và chuẩn hóa văn bản tiếng Việt"""
        # Normalize Unicode
        text = unicodedata.normalize('NFC', text)
        
        # Remove markdown headers
        text = re.sub(r'#+\s*', '', text)
        
        # Clean whitespace and newlines
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Remove extra punctuation
        text = re.sub(r'[^\w\s\.,!?;:]', ' ', text)
        
        return text.strip()
    
    def segment_vietnamese_text(self, text: str) -> List[str]:
        """Tách từ và câu tiếng Việt"""
        if not VIETNAMESE_NLP_AVAILABLE:
            # Fallback to basic sentence splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
        
        try:
            # Sử dụng underthesea để tách câu
            sentences = underthesea.sent_tokenize(text)
            
            # Tách từ cho mỗi câu bằng pyvi
            segmented_sentences = []
            for sentence in sentences:
                if sentence.strip():
                    segmented = ViTokenizer.tokenize(sentence.strip())
                    segmented_sentences.append(segmented)
            
            return segmented_sentences
            
        except Exception as e:
            print(f"Lỗi khi tách từ: {e}")
            # Fallback
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
    
    def create_chunks_with_overlap(self, text: str) -> List[Dict[str, any]]:
        """Chia văn bản thành chunks với overlap"""
        cleaned_text = self.clean_text(text)
        sentences = self.segment_vietnamese_text(cleaned_text)
        
        chunks = []
        current_chunk_sentences = []
        current_word_count = 0
        chunk_id = 0
        
        for sentence in sentences:
            words = sentence.split()
            sentence_word_count = len(words)
            
            # Nếu thêm câu này vào chunk hiện tại vượt quá giới hạn
            if current_word_count + sentence_word_count > self.chunk_size:
                if current_chunk_sentences:  # Nếu chunk hiện tại có nội dung
                    # Tạo chunk
                    chunk_text = ' '.join(current_chunk_sentences)
                    chunk_info = {
                        'id': f'chunk_{chunk_id}',
                        'text': chunk_text,
                        'word_count': current_word_count,
                        'sentence_count': len(current_chunk_sentences),
                        'start_sentence': chunk_id * (len(current_chunk_sentences) - self.chunk_overlap // 50) if chunk_id > 0 else 0
                    }
                    chunks.append(chunk_info)
                    chunk_id += 1
                    
                    # Tạo overlap: giữ lại một số câu cuối
                    overlap_sentences_count = min(self.chunk_overlap // 20, len(current_chunk_sentences))
                    if overlap_sentences_count > 0:
                        overlap_sentences = current_chunk_sentences[-overlap_sentences_count:]
                        overlap_word_count = sum(len(s.split()) for s in overlap_sentences)
                        current_chunk_sentences = overlap_sentences + [sentence]
                        current_word_count = overlap_word_count + sentence_word_count
                    else:
                        current_chunk_sentences = [sentence]
                        current_word_count = sentence_word_count
                else:
                    # Câu đầu tiên của chunk mới
                    current_chunk_sentences = [sentence]
                    current_word_count = sentence_word_count
            else:
                # Thêm câu vào chunk hiện tại
                current_chunk_sentences.append(sentence)
                current_word_count += sentence_word_count
        
        # Thêm chunk cuối cùng nếu có
        if current_chunk_sentences:
            chunk_text = ' '.join(current_chunk_sentences)
            chunk_info = {
                'id': f'chunk_{chunk_id}',
                'text': chunk_text,
                'word_count': current_word_count,
                'sentence_count': len(current_chunk_sentences),
                'start_sentence': chunk_id * (len(current_chunk_sentences) - self.chunk_overlap // 50) if chunk_id > 0 else 0
            }
            chunks.append(chunk_info)
        
        return chunks
    
    def load_and_process_content(self, file_path: str) -> Tuple[List[Dict], Dict]:
        """Load và xử lý file nội dung"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            chunks = self.create_chunks_with_overlap(content)
            
            # Thống kê
            word_counts = [chunk['word_count'] for chunk in chunks]
            stats = {
                'total_chunks': len(chunks),
                'total_words': sum(word_counts),
                'avg_words_per_chunk': np.mean(word_counts),
                'min_words_per_chunk': min(word_counts) if word_counts else 0,
                'max_words_per_chunk': max(word_counts) if word_counts else 0,
                'std_words_per_chunk': np.std(word_counts) if len(word_counts) > 1 else 0
            }
            
            print(f"✅ Đã tạo {stats['total_chunks']} chunks từ {file_path}")
            print(f"📊 Số từ trung bình mỗi chunk: {stats['avg_words_per_chunk']:.1f}")
            print(f"📏 Khoảng từ: {stats['min_words_per_chunk']} - {stats['max_words_per_chunk']} từ")
            
            self.chunks = chunks
            return chunks, stats
            
        except FileNotFoundError:
            print(f"❌ Không tìm thấy file: {file_path}")
            return [], {}
        except Exception as e:
            print(f"❌ Lỗi khi xử lý file: {e}")
            return [], {}
    
    def load_test_suite(self, file_path: str) -> List[Dict]:
        """Load bộ câu hỏi test"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                test_suite = json.load(f)
            
            print(f"✅ Đã load {len(test_suite)} câu hỏi test")
            
            # Validate test suite structure
            required_fields = ['id', 'question', 'expected_chunk', 'category']
            for i, test_case in enumerate(test_suite):
                missing_fields = [field for field in required_fields if field not in test_case]
                if missing_fields:
                    print(f"⚠️  Câu hỏi {i+1} thiếu fields: {missing_fields}")
            
            return test_suite
            
        except FileNotFoundError:
            print(f"❌ Không tìm thấy file test suite: {file_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Lỗi JSON trong test suite: {e}")
            return []
        except Exception as e:
            print(f"❌ Lỗi khi load test suite: {e}")
            return []
    
    def export_chunks_info(self, output_path: str) -> None:
        """Xuất thông tin chunks để debug"""
        if not self.chunks:
            print("⚠️  Không có chunks nào để xuất")
            return
        
        chunks_info = {
            'metadata': {
                'total_chunks': len(self.chunks),
                'chunk_size_limit': self.chunk_size,
                'overlap_size': self.chunk_overlap,
                'processing_timestamp': pd.Timestamp.now().isoformat()
            },
            'chunks': self.chunks
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(chunks_info, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Đã xuất thông tin chunks: {output_path}")
            
        except Exception as e:
            print(f"❌ Lỗi khi xuất chunks info: {e}")

# Utility functions
def validate_vietnamese_text(text: str) -> Dict[str, any]:
    """Validate và phân tích văn bản tiếng Việt"""
    # Check for Vietnamese characters
    vietnamese_chars = re.findall(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]', text)
    
    analysis = {
        'total_chars': len(text),
        'vietnamese_chars': len(vietnamese_chars),
        'vietnamese_ratio': len(vietnamese_chars) / len(text) if text else 0,
        'word_count': len(text.split()),
        'sentence_count': len(re.split(r'[.!?]+', text)),
        'is_vietnamese': len(vietnamese_chars) / len(text) > 0.1 if text else False
    }
    
    return analysis
```

## 🤖 src/embedding_manager.py

```python
import torch
import time
import numpy as np
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Tuple, Optional
import gc
from pathlib import Path

class Qwen3EmbeddingManager:
    """Quản lý embedding model Qwen/Qwen3-Embedding-0.6B tối ưu cho GPU"""
    
    def __init__(self, model_name: str = "Qwen/Qwen3-Embedding-0.6B", 
                 cache_dir: str = "./model_cache"):
        self.model_name = model_name
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # GPU configuration
        self.device = self._detect_device()
        self._setup_gpu_optimization()
        
        # Load model
        self.model = self._load_model()
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        print(f"✅ Model loaded: {model_name}")
        print(f"🔧 Device: {self.device}")
        print(f"📐 Embedding dimension: {self.embedding_dim}")
        
    def _detect_device(self) -> str:
        """Tự động phát hiện device phù hợp"""
        if torch.cuda.is_available():
            device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            total_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"🚀 GPU detected: {gpu_name}")
            print(f"💾 GPU memory: {total_memory:.1f} GB")
        elif torch.backends.mps.is_available():
            device = "mps"  # Apple Silicon
            print("🍎 Apple Silicon MPS detected")
        else:
            device = "cpu"
            print("💻 Using CPU")
        
        return device
    
    def _setup_gpu_optimization(self) -> None:
        """Cài đặt tối ưu GPU"""
        if self.device == "cuda":
            # Enable TensorFloat-32 for better performance on Ampere GPUs
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            
            # Optimize memory allocation
            torch.cuda.empty_cache()
            
            # Set memory fraction if needed
            available_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            if available_memory < 8:  # Less than 8GB
                torch.cuda.set_per_process_memory_fraction(0.8)
                print("⚡ GPU memory optimization enabled for <8GB GPU")
    
    def _load_model(self) -> SentenceTransformer:
        """Load Qwen3 embedding model với error handling"""
        try:
            print(f"📥 Loading model: {self.model_name}...")
            start_time = time.time()
            
            model = SentenceTransformer(
                self.model_name,
                device=self.device,
                cache_folder=str(self.cache_dir),
                trust_remote_code=True  # Required for Qwen models
            )
            
            load_time = time.time() - start_time
            print(f"✅ Model loaded successfully in {load_time:.2f}s")
            
            return model
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("💡 Tip: Ensure you have internet connection and sufficient disk space")
            raise
    
    def get_model_info(self) -> Dict[str, any]:
        """Lấy thông tin model"""
        info = {
            'name': self.model_name,
            'device': self.device,
            'embedding_dimension': self.embedding_dim,
            'max_seq_length': getattr(self.model, 'max_seq_length', 512),
            'model_size_mb': self._estimate_model_size(),
            'supports_batch': True
        }
        
        if self.device == "cuda":
            info.update({
                'gpu_name': torch.cuda.get_device_name(0),
                'gpu_memory_total': torch.cuda.get_device_properties(0).total_memory / 1e9

            })
        
        return info
    
    def _estimate_model_size(self) -> float:
        """Ước tính kích thước model (MB)"""
        try:
            total_params = sum(p.numel() for p in self.model.parameters())
            # Giả sử float32 (4 bytes per parameter)
            size_mb = (total_params * 4) / (1024 * 1024)
            return round(size_mb, 1)
        except:
            return 0.0
    
    def encode_texts(self, texts: List[str], batch_size: int = 32, 
                    show_progress: bool = True, normalize: bool = True) -> np.ndarray:
        """Encode danh sách texts thành embeddings"""
        if not texts:
            return np.empty((0, self.embedding_dim))
        
        print(f"🔄 Encoding {len(texts)} texts...")
        start_time = time.time()
        
        # Tối ưu batch size cho GPU
        optimal_batch_size = self._get_optimal_batch_size(batch_size)
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=optimal_batch_size,
                show_progress_bar=show_progress,
                convert_to_tensor=False,  # Return numpy array
                normalize_embeddings=normalize,
                device=self.device
            )
            
            encode_time = time.time() - start_time
            speed = len(texts) / encode_time
            
            print(f"✅ Encoding completed in {encode_time:.2f}s")
            print(f"⚡ Speed: {speed:.1f} texts/second")
            print(f"📊 Shape: {embeddings.shape}")
            
            return embeddings
            
        except Exception as e:
            print(f"❌ Error during encoding: {e}")
            raise
    
    def _get_optimal_batch_size(self, requested_batch_size: int) -> int:
        """Tính toán batch size tối ưu dựa trên GPU memory"""
        if self.device == "cpu":
            return min(requested_batch_size, 16)
        
        if self.device == "cuda":
            available_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            
            if available_memory < 4:
                return min(requested_batch_size, 8)
            elif available_memory < 8:
                return min(requested_batch_size, 16)
            elif available_memory < 12:
                return min(requested_batch_size, 32)
            else:
                return min(requested_batch_size, 64)
        
        return requested_batch_size
    
    def find_most_similar(self, query_embedding: np.ndarray, 
                         corpus_embeddings: np.ndarray, 
                         top_k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """Tìm top-k embeddings tương đồng nhất"""
        try:
            # Convert to torch tensors for GPU computation
            query_tensor = torch.tensor(query_embedding, device=self.device)
            corpus_tensor = torch.tensor(corpus_embeddings, device=self.device)
            
            # Tính cosine similarity
            similarities = util.cos_sim(query_tensor, corpus_tensor)
            
            # Lấy top-k results
            top_k = min(top_k, corpus_embeddings.shape[0])
            top_results = torch.topk(similarities, k=top_k, dim=-1)
            
            # Convert về numpy
            indices = top_results.indices.cpu().numpy().flatten()
            scores = top_results.values.cpu().numpy().flatten()
            
            return indices, scores
            
        except Exception as e:
            print(f"❌ Error in similarity search: {e}")
            raise
    
    def batch_similarity_search(self, queries: List[str], 
                               corpus_embeddings: np.ndarray,
                               corpus_ids: List[str],
                               top_k: int = 5) -> List[Dict]:
        """Thực hiện batch similarity search"""
        print(f"🔍 Running batch search for {len(queries)} queries...")
        
        # Encode all queries at once
        query_embeddings = self.encode_texts(queries, show_progress=False)
        
        results = []
        for i, (query, query_emb) in enumerate(zip(queries, query_embeddings)):
            # Find similar chunks for this query
            indices, scores = self.find_most_similar(
                query_emb.reshape(1, -1), 
                corpus_embeddings, 
                top_k
            )
            
            # Build result
            search_results = []
            for idx, score in zip(indices, scores):
                search_results.append({
                    'chunk_id': corpus_ids[idx],
                    'similarity_score': float(score),
                    'rank': len(search_results) + 1
                })
            
            results.append({
                'query_id': i,
                'query': query,
                'results': search_results
            })
        
        return results
    
    def get_memory_stats(self) -> Dict[str, any]:
        """Lấy thống kê memory usage"""
        stats = {'device': self.device}
        
        if self.device == "cuda":
            stats.update({
                'allocated_gb': torch.cuda.memory_allocated() / 1e9,
                'cached_gb': torch.cuda.memory_reserved() / 1e9,
                'max_allocated_gb': torch.cuda.max_memory_allocated() / 1e9,
                'gpu_name': torch.cuda.get_device_name(0)
            })
        
        return stats
    
    def cleanup(self) -> None:
        """Dọn dẹp memory và cache"""
        if self.device == "cuda":
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
        
        # Force garbage collection
        gc.collect()
        
        print("🧹 Memory cleanup completed")
```

## 📊 src/metrics.py

```python
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import json

class EmbeddingMetrics:
    """Tính toán metrics cho embedding model evaluation"""
    
    def __init__(self):
        self.metrics_names = [
            'MRR', 'Hit_Rate@1', 'Hit_Rate@3', 'Hit_Rate@5', 
            'MAP@5', 'NDCG@5', 'Precision@5', 'Recall@5'
        ]
    
    def calculate_mrr(self, search_results: List[Dict], ground_truth: List[Dict]) -> float:
        """Tính Mean Reciprocal Rank"""
        reciprocal_ranks = []
        
        for i, result in enumerate(search_results):
            query_id = result.get('query_id', i)
            search_result_ids = [r['chunk_id'] for r in result['results']]
            
            # Tìm ground truth cho query này
            expected_chunk = None
            for gt in ground_truth:
                if gt.get('id', gt.get('query_id')) == query_id + 1:  # +1 vì ground truth bắt đầu từ 1
                    expected_chunk = gt['expected_chunk']
                    break
            
            if not expected_chunk:
                reciprocal_ranks.append(0.0)
                continue
            
            # Tìm rank của expected chunk
            rank = None
            for j, chunk_id in enumerate(search_result_ids):
                if self._chunk_matches(chunk_id, expected_chunk):
                    rank = j + 1
                    break
            
            reciprocal_rank = 1.0 / rank if rank else 0.0
            reciprocal_ranks.append(reciprocal_rank)
        
        return np.mean(reciprocal_ranks) if reciprocal_ranks else 0.0
    
    def calculate_hit_rate_at_k(self, search_results: List[Dict], 
                               ground_truth: List[Dict], k: int) -> float:
        """Tính Hit Rate@k"""
        hits = 0
        total_queries = len(search_results)
        
        for i, result in enumerate(search_results):
            query_id = result.get('query_id', i)
            top_k_results = result['results'][:k]
            top_k_ids = [r['chunk_id'] for r in top_k_results]
            
            # Tìm ground truth
            expected_chunk = None
            for gt in ground_truth:
                if gt.get('id', gt.get('query_id')) == query_id + 1:
                    expected_chunk = gt['expected_chunk']
                    break
            
            if expected_chunk:
                for chunk_id in top_k_ids:
                    if self._chunk_matches(chunk_id, expected_chunk):
                        hits += 1
                        break
        
        return hits / total_queries if total_queries > 0 else 0.0
    
    def calculate_precision_at_k(self, search_results: List[Dict],
                                ground_truth: List[Dict], k: int) -> float:
        """Tính Precision@k"""
        precisions = []
        
        for i, result in enumerate(search_results):
            query_id = result.get('query_id', i)
            top_k_results = result['results'][:k]
            top_k_ids = [r['chunk_id'] for r in top_k_results]
            
            # Tìm ground truth
            expected_chunk = None
            for gt in ground_truth:
                if gt.get('id', gt.get('query_id')) == query_id + 1:
                    expected_chunk = gt['expected_chunk']
                    break
            
            if not expected_chunk:
                precisions.append(0.0)
                continue
            
            # Đếm relevant documents trong top-k
            relevant_count = 0
            for chunk_id in top_k_ids:
                if self._chunk_matches(chunk_id, expected_chunk):
                    relevant_count += 1
            
            precision = relevant_count / len(top_k_ids) if top_k_ids else 0.0
            precisions.append(precision)
        
        return np.mean(precisions) if precisions else 0.0
    
    def calculate_recall_at_k(self, search_results: List[Dict],
                             ground_truth: List[Dict], k: int) -> float:
        """Tính Recall@k (trong trường hợp này mỗi query chỉ có 1 relevant doc)"""
        return self.calculate_hit_rate_at_k(search_results, ground_truth, k)
    
    def calculate_ndcg_at_k(self, search_results: List[Dict],
                           ground_truth: List[Dict], k: int) -> float:
        """Tính Normalized Discounted Cumulative Gain@k"""
        ndcg_scores = []
        
        for i, result in enumerate(search_results):
            query_id = result.get('query_id', i)
            top_k_results = result['results'][:k]
            
            # Tìm ground truth
            expected_chunk = None
            for gt in ground_truth:
                if gt.get('id', gt.get('query_id')) == query_id + 1:
                    expected_chunk = gt['expected_chunk']
                    break
            
            if not expected_chunk:
                ndcg_scores.append(0.0)
                continue
            
            # Tính DCG
            dcg = 0.0
            for j, chunk_result in enumerate(top_k_results):
                if self._chunk_matches(chunk_result['chunk_id'], expected_chunk):
                    relevance = 1  # Binary relevance
                    dcg += relevance / np.log2(j + 2)  # j+2 vì log2(1) = 0
            
            # IDCG (trong trường hợp này là 1.0 vì chỉ có 1 relevant doc)
            idcg = 1.0
            
            ndcg = dcg / idcg if idcg > 0 else 0.0
            ndcg_scores.append(ndcg)
        
        return np.mean(ndcg_scores) if ndcg_scores else 0.0
    
    def calculate_map_at_k(self, search_results: List[Dict],
                          ground_truth: List[Dict], k: int) -> float:
        """Tính Mean Average Precision@k"""
        ap_scores = []
        
        for i, result in enumerate(search_results):
            query_id = result.get('query_id', i)
            top_k_results = result['results'][:k]
            
            # Tìm ground truth
            expected_chunk = None
            for gt in ground_truth:
                if gt.get('id', gt.get('query_id')) == query_id + 1:
                    expected_chunk = gt['expected_chunk']
                    break
            
            if not expected_chunk:
                ap_scores.append(0.0)
                continue
            
            # Tính Average Precision
            relevant_positions = []
            for j, chunk_result in enumerate(top_k_results):
                if self._chunk_matches(chunk_result['chunk_id'], expected_chunk):
                    relevant_positions.append(j + 1)
            
            if not relevant_positions:
                ap_scores.append(0.0)
                continue
            
            # Tính precision tại mỗi relevant position
            precision_at_relevant = []
            for pos in relevant_positions:
                precision_at_relevant.append(1.0 / pos)  # Trong binary case
            
            ap = np.mean(precision_at_relevant) if precision_at_relevant else 0.0
            ap_scores.append(ap)
        
        return np.mean(ap_scores) if ap_scores else 0.0
    
    def _chunk_matches(self, chunk_id: str, expected_chunk: str) -> bool:
        """Kiểm tra xem chunk_id có match với expected_chunk không"""
        # Normalize strings for comparison
        chunk_id_clean = chunk_id.lower().replace('_', ' ').replace('-', ' ')
        expected_clean = expected_chunk.lower().replace('_', ' ').replace('-', ' ')
        
        # Check if any significant word from expected appears in chunk_id
        expected_words = expected_clean.split()
        return any(word in chunk_id_clean for word in expected_words if len(word) > 3)
    
    def calculate_all_metrics(self, search_results: List[Dict], 
                             ground_truth: List[Dict]) -> Dict[str, float]:
        """Tính tất cả metrics"""
        metrics = {}
        
        try:
            metrics['MRR'] = self.calculate_mrr(search_results, ground_truth)
            metrics['Hit_Rate@1'] = self.calculate_hit_rate_at_k(search_results, ground_truth, 1)
            metrics['Hit_Rate@3'] = self.calculate_hit_rate_at_k(search_results, ground_truth, 3)
            metrics['Hit_Rate@5'] = self.calculate_hit_rate_at_k(search_results, ground_truth, 5)
            metrics['Precision@5'] = self.calculate_precision_at_k(search_results, ground_truth, 5)
            metrics['Recall@5'] = self.calculate_recall_at_k(search_results, ground_truth, 5)
            metrics['NDCG@5'] = self.calculate_ndcg_at_k(search_results, ground_truth, 5)
            metrics['MAP@5'] = self.calculate_map_at_k(search_results, ground_truth, 5)
            
        except Exception as e:
            print(f"❌ Error calculating metrics: {e}")
            # Return zero metrics in case of error
            metrics = {metric: 0.0 for metric in self.metrics_names}
        
        return metrics
    
    def generate_detailed_analysis(self, search_results: List[Dict],
                                  ground_truth: List[Dict]) -> Tuple[Dict, pd.DataFrame]:
        """Tạo phân tích chi tiết cho từng query"""
        detailed_results = []
        
        for i, result in enumerate(search_results):
            query_id = result.get('query_id', i)
            query_text = result['query']
            search_result_ids = [r['chunk_id'] for r in result['results']]
            scores = [r['similarity_score'] for r in result['results']]
            
            # Tìm ground truth
            expected_chunk = None
            category = "unknown"
            for gt in ground_truth:
                if gt.get('id', gt.get('query_id')) == query_id + 1:
                    expected_chunk = gt['expected_chunk']
                    category = gt.get('category', 'unknown')
                    break
            
            # Tìm rank của correct answer
            found_rank = None
            correct_score = 0.0
            if expected_chunk:
                for j, chunk_id in enumerate(search_result_ids):
                    if self._chunk_matches(chunk_id, expected_chunk):
                        found_rank = j + 1
                        correct_score = scores[j] if j < len(scores) else 0.0
                        break
            
            detailed_result = {
                'query_id': query_id + 1,
                'query': query_text[:100] + "..." if len(query_text) > 100 else query_text,
                'category': category,
                'expected_chunk': expected_chunk,
                'found_rank': found_rank,
                'correct_score': correct_score,
                'top_1_score': scores[0] if scores else 0.0,
                'score_gap': scores[0] - correct_score if scores and correct_score > 0 else 0.0,
                'hit@1': 1 if found_rank == 1 else 0,
                'hit@3': 1 if found_rank and found_rank <= 3 else 0,
                'hit@5': 1 if found_rank and found_rank <= 5 else 0,
            }
            
            detailed_results.append(detailed_result)
        
        # Tạo DataFrame
        df = pd.DataFrame(detailed_results)
        
        # Tính summary metrics
        summary_metrics = self.calculate_all_metrics(search_results, ground_truth)
        
        return summary_metrics, df
    
    def analyze_performance_by_category(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Phân tích performance theo category"""
        if 'category' not in df.columns:
            return {}
        
        category_analysis = {}
        
        for category in df['category'].unique():
            category_df = df[df['category'] == category]
            
            analysis = {
                'total_queries': len(category_df),
                'hit_rate@1': category_df['hit@1'].mean(),
                'hit_rate@3': category_df['hit@3'].mean(),
                'hit_rate@5': category_df['hit@5'].mean(),
                'avg_rank': category_df[category_df['found_rank'].notna()]['found_rank'].mean(),
                'avg_correct_score': category_df[category_df['correct_score'] > 0]['correct_score'].mean(),
                'questions_not_found': len(category_df[category_df['found_rank'].isna()])
            }
            
            category_analysis[category] = analysis
        
        return category_analysis
```

## 📈 src/visualizer.py

```python
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

# Cấu hình matplotlib cho tiếng Việt
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Tahoma', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")

class BenchmarkVisualizer:
    """Tạo visualizations cho benchmark results"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Tạo thư mục con
        self.charts_dir = self.output_dir / "charts"
        self.charts_dir.mkdir(exist_ok=True)
        
        # Color palette
        self.colors = px.colors.qualitative.Set2
        
    def create_metrics_overview(self, metrics: Dict[str, float], 
                               save_path: Optional[str] = None) -> None:
        """Tạo overview chart của các metrics"""
        
        # Prepare data
        metric_names = list(metrics.keys())
        metric_values = list(metrics.values())
        
        # Create figure with subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Overall Metrics', 'Hit Rates', 'Precision & Recall', 'Advanced Metrics'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Overall metrics (bar chart)
        fig.add_trace(
            go.Bar(
                x=metric_names,
                y=metric_values,
                name="All Metrics",
                marker_color=self.colors[0],
                text=[f"{v:.3f}" for v in metric_values],
                textposition='outside'
            ),
            row=1, col=1
        )
        
        # Hit rates
        hit_metrics = {k: v for k, v in metrics.items() if 'Hit_Rate' in k}
        if hit_metrics:
            fig.add_trace(
                go.Bar(
                    x=list(hit_metrics.keys()),
                    y=list(hit_metrics.values()),
                    name="Hit Rates",
                    marker_color=self.colors[1],
                    text=[f"{v:.2%}" for v in hit_metrics.values()],
                    textposition='outside'
                ),
                row=1, col=2
            )
        
        # Precision & Recall
        pr_metrics = {k: v for k, v in metrics.items() if any(x in k for x in ['Precision', 'Recall'])}
        if pr_metrics:
            fig.add_trace(
                go.Bar(
                    x=list(pr_metrics.keys()),
                    y=list(pr_metrics.values()),
                    name="Precision & Recall",
                    marker_color=self.colors[2],
                    text=[f"{v:.3f}" for v in pr_metrics.values()],
                    textposition='outside'
                ),
                row=2, col=1
            )
        
        # Advanced metrics
        advanced_metrics = {k: v for k, v in metrics.items() if k in ['MRR', 'MAP@5', 'NDCG@5']}
        if advanced_metrics:
            fig.add_trace(
                go.Bar(
                    x=list(advanced_metrics.keys()),
                    y=list(advanced_metrics.values()),
                    name="Advanced Metrics",
                    marker_color=self.colors[3],
                    text=[f"{v:.3f}" for v in advanced_metrics.values()],
                    textposition='outside'
                ),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title_text="Qwen3-Embedding-0.6B Performance Overview",
            height=800,
            showlegend=False
        )
        
        # Save plot
        if save_path is None:
            save_path = self.charts_dir / "metrics_overview.html"
        
        fig.write_html(str(save_path))
        print(f"📊 Metrics overview saved: {save_path}")
    
    def create_detailed_analysis_chart(self, df: pd.DataFrame,
                                      save_path: Optional[str] = None) -> None:
        """Tạo chart phân tích chi tiết"""
        
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                'Query Difficulty Distribution', 'Score Distribution', 
                'Performance by Category', 'Rank Distribution',
                'Score Gap Analysis', 'Success Rate by Rank'
            ),
            specs=[[{"type": "pie"}, {"type": "histogram"}],
                   [{"type": "bar"}, {"type": "histogram"}],
                   [{"type": "histogram"}, {"type": "bar"}]]
        )
        
        # 1. Query difficulty (dựa trên found_rank)
        difficulty_labels = []
        difficulty_values = []
        
        easy_count = len(df[df['found_rank'] == 1])
        medium_count = len(df[(df['found_rank'] > 1) & (df['found_rank'] <= 3)])
        hard_count = len(df[(df['found_rank'] > 3) & (df['found_rank'] <= 5)])
        very_hard_count = len(df[df['found_rank'].isna()])
        
        for label, count in [('Easy (Rank 1)', easy_count), ('Medium (Rank 2-3)', medium_count),
                            ('Hard (Rank 4-5)', hard_count), ('Very Hard (Not Found)', very_hard_count)]:
            if count > 0:
                difficulty_labels.append(label)
                difficulty_values.append(count)
        
        fig.add_trace(
            go.Pie(
                labels=difficulty_labels,
                values=difficulty_values,
                name="Difficulty"
            ),
            row=1, col=1
        )
        
        # 2. Score distribution
        all_scores = df['top_1_score'].tolist() + df[df['correct_score'] > 0]['correct_score'].tolist()
        fig.add_trace(
            go.Histogram(
                x=all_scores,
                name="Scores",
                nbinsx=20,
                marker_color=self.colors[1]
            ),
            row=1, col=2
        )
        
        # 3. Performance by category
        if 'category' in df.columns:
            category_performance = df.groupby('category')['hit@5'].mean().reset_index()
            fig.add_trace(
                go.Bar(
                    x=category_performance['category'],
                    y=category_performance['hit@5'],
                    name="Hit@5 by Category",
                    marker_color=self.colors[2],
                    text=[f"{v:.1%}" for v in category_performance['hit@5']],
                    textposition='outside'
                ),
                row=2, col=1
            )
        
        # 4. Rank distribution
        rank_counts = df[df['found_rank'].notna()]['found_rank'].value_counts().sort_index()
        fig.add_trace(
            go.Bar(
                x=[f"Rank {int(r)}" for r in rank_counts.index],
                y=rank_counts.values,
                name="Rank Distribution",
                marker_color=self.colors[3]
            ),
            row=2, col=2
        )
        
        # 5. Score gap analysis
        score_gaps = df[df['score_gap'] != 0]['score_gap']
        if len(score_gaps) > 0:
            fig.add_trace(
                go.Histogram(
                    x=score_gaps,
                    name="Score Gap",
                    nbinsx=15,
                    marker_color=self.colors[4]
                ),
                row=2, col=3
            )
        
        # Update layout
        fig.update_layout(
            title_text="Detailed Performance Analysis",
            height=1000,
            showlegend=False
        )
        
        if save_path is None:
            save_path = self.charts_dir / "detailed_analysis.html"
        
        fig.write_html(str(save_path))
        print(f"📈 Detailed analysis saved: {save_path}")
    
    def create_performance_radar(self, metrics: Dict[str, float],
                                save_path: Optional[str] = None) -> None:
        """Tạo radar chart cho performance metrics"""
        
        # Select key metrics for radar
        radar_metrics = ['MRR', 'Hit_Rate@1', 'Hit_Rate@5', 'Precision@5', 'Recall@5', 'NDCG@5']
        
        categories = []
        values = []
        
        for metric in radar_metrics:
            if metric in metrics:
                categories.append(metric)
                values.append(metrics[metric])
        
        # Add first value at the end to close the radar
        if categories:
            categories.append(categories[0])
            values.append(values[0])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Qwen3-Embedding-0.6B',
            line_color=self.colors[0]
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title="Performance Radar Chart",
            showlegend=True
        )
        
        if save_path is None:
            save_path = self.charts_dir / "performance_radar.html"
        
        fig.write_html(str(save_path))
        print(f"🎯 Radar chart saved: {save_path}")
    
    def create_category_performance_chart(self, category_analysis: Dict[str, Dict],
                                         save_path: Optional[str] = None) -> None:
        """Tạo chart performance theo category"""
        
        if not category_analysis:
            print("⚠️ No category analysis data available")
            return
        
        categories = list(category_analysis.keys())
        hit_1_rates = [category_analysis[cat]['hit_rate@1'] for cat in categories]
        hit_3_rates = [category_analysis[cat]['hit_rate@3'] for cat in categories]
        hit_5_rates = [category_analysis[cat]['hit_rate@5'] for cat in categories]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Hit Rate@1',
            x=categories,
            y=hit_1_rates,
            marker_color=self.colors[0],
            text=[f"{v:.1%}" for v in hit_1_rates],
            textposition='outside'
        ))
                
        fig.add_trace(go.Bar(
            name='Hit Rate@5',
            x=categories,
            y=hit_5_rates,
            marker_color=self.colors[2],
            text=[f"{v:.1%}" for v in hit_5_rates],
            textposition='outside'
        ))
        
        fig.update_layout(
            title='Performance by Question Category',
            xaxis_title='Category',
            yaxis_title='Hit Rate',
            barmode='group',
            height=600
        )
        
        if save_path is None:
            save_path = self.charts_dir / "category_performance.html"
        
        fig.write_html(str(save_path))
        print(f"📊 Category performance chart saved: {save_path}")
    
    def generate_html_report(self, results: Dict, save_path: Optional[str] = None) -> None:
        """Tạo báo cáo HTML tổng hợp"""
        
        html_template = """
        <!DOCTYPE html>
        <html lang="vi">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Qwen3-Embedding-0.6B Benchmark Report</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 40px; 
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }
                h1, h2, h3 { 
                    color: #2c3e50; 
                }
                .header {
                    text-align: center;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }
                .metrics-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }
                .metric-card {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                }
                .metric-value {
                    font-size: 2em;
                    font-weight: bold;
                }
                .metric-name {
                    font-size: 0.9em;
                    opacity: 0.9;
                }
                table { 
                    border-collapse: collapse; 
                    width: 100%; 
                    margin: 20px 0; 
                }
                th, td { 
                    border: 1px solid #ddd; 
                    padding: 12px; 
                    text-align: left; 
                }
                th { 
                    background-color: #3498db;
                    color: white;
                    font-weight: bold; 
                }
                .excellent { background-color: #d4edda; }
                .good { background-color: #e2f3ff; }
                .average { background-color: #fff3cd; }
                .poor { background-color: #f8d7da; }
                .summary {
                    background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
                    color: white;
                    padding: 25px;
                    border-radius: 10px;
                    margin: 30px 0;
                }
                .charts-section {
                    margin: 30px 0;
                    text-align: center;
                }
                .chart-link {
                    display: inline-block;
                    margin: 10px;
                    padding: 10px 20px;
                    background-color: #3498db;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }
                .chart-link:hover {
                    background-color: #2980b9;
                }
                .footer {
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    text-align: center;
                    color: #666;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🇻🇳 Vietnamese Embedding Model Benchmark</h1>
                    <h2>Qwen/Qwen3-Embedding-0.6B Performance Report</h2>
                    <p><strong>Generated:</strong> {timestamp}</p>
                </div>

                <div class="summary">
                    <h2>📋 Executive Summary</h2>
                    <p>The Qwen3-Embedding-0.6B model was evaluated on {total_queries} Vietnamese queries across {total_categories} categories. 
                    The model achieved an overall MRR of <strong>{mrr:.3f}</strong> and Hit Rate@5 of <strong>{hit_rate_5:.1%}</strong>.</p>
                </div>

                <h2>📊 Key Performance Metrics</h2>
                <div class="metrics-grid">
                    {metrics_cards}
                </div>

                <h2>🎯 Performance Analysis</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Score</th>
                        <th>Performance Level</th>
                        <th>Interpretation</th>
                    </tr>
                    {metrics_table}
                </table>

                <h2>📈 Detailed Results</h2>
                {detailed_table}

                <h2>📊 Interactive Charts</h2>
                <div class="charts-section">
                    <a href="charts/metrics_overview.html" class="chart-link">📊 Metrics Overview</a>
                    <a href="charts/detailed_analysis.html" class="chart-link">📈 Detailed Analysis</a>
                    <a href="charts/performance_radar.html" class="chart-link">🎯 Performance Radar</a>
                    <a href="charts/category_performance.html" class="chart-link">📋 Category Performance</a>
                </div>

                <h2>💡 Recommendations</h2>
                <div class="summary">
                    {recommendations}
                </div>

                <div class="footer">
                    <p>Report generated by Vietnamese Embedding Benchmark Tool</p>
                    <p>Model: Qwen/Qwen3-Embedding-0.6B | Hardware: {device_info}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Extract data from results
        metrics = results.get('metrics', {})
        model_info = results.get('model_info', {})
        detailed_df = results.get('detailed_analysis', pd.DataFrame())
        category_analysis = results.get('category_analysis', {})
        
        # Generate metrics cards
        metrics_cards = ""
        for metric_name, metric_value in metrics.items():
            if isinstance(metric_value, (int, float)):
                if 'Rate' in metric_name:
                    display_value = f"{metric_value:.1%}"
                else:
                    display_value = f"{metric_value:.3f}"
                
                metrics_cards += f"""
                <div class="metric-card">
                    <div class="metric-value">{display_value}</div>
                    <div class="metric-name">{metric_name}</div>
                </div>
                """
        
        # Generate metrics table
        def get_performance_level(metric_name: str, value: float) -> tuple:
            if 'Hit_Rate' in metric_name or 'Recall' in metric_name or 'Precision' in metric_name:
                if value >= 0.8: return "excellent", "Excellent"
                elif value >= 0.6: return "good", "Good"
                elif value >= 0.4: return "average", "Average"
                else: return "poor", "Poor"
            elif metric_name in ['MRR', 'MAP@5', 'NDCG@5']:
                if value >= 0.7: return "excellent", "Excellent"
                elif value >= 0.5: return "good", "Good"
                elif value >= 0.3: return "average", "Average"
                else: return "poor", "Poor"
            return "average", "Average"
        
        metrics_table = ""
        interpretations = {
            'MRR': 'Average position of first correct answer',
            'Hit_Rate@1': 'Percentage of queries with correct answer in top 1',
            'Hit_Rate@5': 'Percentage of queries with correct answer in top 5',
            'Precision@5': 'Precision of top 5 results',
            'Recall@5': 'Recall of top 5 results',
            'NDCG@5': 'Ranking quality considering positions',
            'MAP@5': 'Mean average precision at 5'
        }
        
        for metric_name, metric_value in metrics.items():
            if isinstance(metric_value, (int, float)):
                class_name, level = get_performance_level(metric_name, metric_value)
                if 'Rate' in metric_name:
                    display_value = f"{metric_value:.1%}"
                else:
                    display_value = f"{metric_value:.3f}"
                
                interpretation = interpretations.get(metric_name, "Performance metric")
                
                metrics_table += f"""
                <tr class="{class_name}">
                    <td><strong>{metric_name}</strong></td>
                    <td>{display_value}</td>
                    <td>{level}</td>
                    <td>{interpretation}</td>
                </tr>
                """
        
        # Generate detailed table
        detailed_table = ""
        if not detailed_df.empty:
            detailed_table = detailed_df.to_html(classes='table', escape=False, index=False)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, category_analysis)
        
        # Fill template
        html_content = html_template.format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            total_queries=len(detailed_df) if not detailed_df.empty else 0,
            total_categories=len(category_analysis),
            mrr=metrics.get('MRR', 0),
            hit_rate_5=metrics.get('Hit_Rate@5', 0),
            metrics_cards=metrics_cards,
            metrics_table=metrics_table,
            detailed_table=detailed_table,
            recommendations=recommendations,
            device_info=model_info.get('device', 'Unknown')
        )
        
        if save_path is None:
            save_path = self.output_dir / "benchmark_report.html"
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📋 HTML report saved: {save_path}")
    
    def _generate_recommendations(self, metrics: Dict[str, float], 
                                 category_analysis: Dict) -> str:
        """Tạo recommendations dựa trên results"""
        recommendations = []
        
        # Overall performance assessment
        mrr = metrics.get('MRR', 0)
        hit_rate_5 = metrics.get('Hit_Rate@5', 0)
        
        if mrr >= 0.7 and hit_rate_5 >= 0.8:
            recommendations.append("✅ <strong>Excellent Performance:</strong> The model shows excellent performance across all metrics and is ready for production deployment.")
        elif mrr >= 0.5 and hit_rate_5 >= 0.6:
            recommendations.append("✅ <strong>Good Performance:</strong> The model performs well and can be used for production with some optimizations.")
        else:
            recommendations.append("⚠️ <strong>Performance Issues:</strong> The model shows room for improvement. Consider fine-tuning or using additional preprocessing.")
        
        # Category-specific recommendations
        if category_analysis:
            worst_category = min(category_analysis.keys(), 
                               key=lambda x: category_analysis[x].get('hit_rate@5', 0))
            worst_score = category_analysis[worst_category].get('hit_rate@5', 0)
            
            if worst_score < 0.5:
                recommendations.append(f"🎯 <strong>Category Improvement:</strong> The '{worst_category}' category shows the lowest performance ({worst_score:.1%}). Consider adding more training data for this category.")
        
        # Technical recommendations
        if hit_rate_5 < 0.7:
            recommendations.append("🔧 <strong>Technical Improvements:</strong> Consider increasing chunk overlap, experimenting with different chunking strategies, or using hybrid search approaches.")
        
        if metrics.get('Hit_Rate@1', 0) < 0.4:
            recommendations.append("📚 <strong>Data Quality:</strong> Low top-1 accuracy suggests data quality issues. Review document preprocessing and ensure clear question-answer relationships.")
        
        return "<br>".join(recommendations)
```

## 🚀 benchmark.py (Main Script)

```python
#!/usr/bin/env python3
"""
Vietnamese Embedding Model Benchmark Tool
Model: Qwen/Qwen3-Embedding-0.6B

Usage: python benchmark.py [--config configs/model_config.json]
"""

import argparse
import json
import time
from pathlib import Path
import pandas as pd
from datetime import datetime
import traceback

from src.data_processor import VietnameseTextProcessor
from src.embedding_manager import Qwen3EmbeddingManager  
from src.metrics import EmbeddingMetrics
from src.visualizer import BenchmarkVisualizer

class Qwen3Benchmark:
    """Main benchmark class for Qwen3-Embedding-0.6B"""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.reports_dir = Path(self.config['output']['reports_dir'])
        self.reports_dir.mkdir(exist_ok=True)
        
        print("🇻🇳 Vietnamese Embedding Benchmark Tool")
        print("=" * 60)
        print(f"Model: {self.config['model']['name']}")
        print(f"Reports directory: {self.reports_dir.absolute()}")
        print("=" * 60)
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"✅ Configuration loaded from {config_path}")
            return config
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            raise
    
    def run_benchmark(self) -> dict:
        """Execute complete benchmark pipeline"""
        benchmark_start = time.time()
        results = {
            'benchmark_info': {
                'model_name': self.config['model']['name'],
                'start_time': datetime.now().isoformat(),
                'config': self.config
            }
        }
        
        try:
            # Step 1: Process data
            print("\n📚 STEP 1: Processing Vietnamese text data")
            print("-" * 40)
            
            processor = VietnameseTextProcessor(
                chunk_size=self.config['evaluation']['chunk_size'],
                chunk_overlap=self.config['evaluation']['chunk_overlap']
            )
            
            chunks, data_stats = processor.load_and_process_content('data/content.md')
            if not chunks:
                raise ValueError("No chunks were created from content data")
            
            test_suite = processor.load_test_suite('data/test_suite.json')
            if not test_suite:
                raise ValueError("No test questions were loaded")
            
            results['data_stats'] = data_stats
            results['test_suite_size'] = len(test_suite)
            
            # Export chunks info for debugging
            processor.export_chunks_info(self.reports_dir / "chunks_info.json")
            
            # Step 2: Initialize embedding model
            print("\n🤖 STEP 2: Loading embedding model")
            print("-" * 40)
            
            embedding_manager = Qwen3EmbeddingManager(
                model_name=self.config['model']['name']
            )
            
            model_info = embedding_manager.get_model_info()
            results['model_info'] = model_info
            
            print(f"📐 Model info: {model_info}")
            
            # Step 3: Generate embeddings
            print("\n🔄 STEP 3: Generating embeddings")
            print("-" * 40)
            
            chunk_texts = [chunk['text'] for chunk in chunks]
            chunk_ids = [chunk['id'] for chunk in chunks]
            
            embedding_start = time.time()
            corpus_embeddings = embedding_manager.encode_texts(
                chunk_texts,
                batch_size=self.config['model']['batch_size'],
                normalize=self.config['model']['normalize_embeddings']
            )
            embedding_time = time.time() - embedding_start
            
            results['embedding_time_seconds'] = embedding_time
            results['embedding_speed_texts_per_second'] = len(chunk_texts) / embedding_time
            
            print(f"⚡ Embedding generation completed in {embedding_time:.2f}s")
            print(f"📊 Speed: {results['embedding_speed_texts_per_second']:.1f} texts/second")
            
            # Step 4: Run similarity search evaluation
            print("\n🔍 STEP 4: Running similarity search evaluation")
            print("-" * 40)
            
            queries = [test['question'] for test in test_suite]
            
            search_start = time.time()
            search_results = embedding_manager.batch_similarity_search(
                queries=queries,
                corpus_embeddings=corpus_embeddings,
                corpus_ids=chunk_ids,
                top_k=self.config['evaluation']['top_k']
            )
            search_time = time.time() - search_start
            
            results['search_time_seconds'] = search_time
            results['search_speed_queries_per_second'] = len(queries) / search_time
            results['search_results'] = search_results
            
            print(f"🔍 Search completed in {search_time:.2f}s")
            print(f"⚡ Search speed: {results['search_speed_queries_per_second']:.1f} queries/second")
            
            # Step 5: Calculate metrics
            print("\n📊 STEP 5: Calculating performance metrics")
            print("-" * 40)
            
            metrics_calculator = EmbeddingMetrics()
            
            # Calculate all metrics
            metrics = metrics_calculator.calculate_all_metrics(search_results, test_suite)
            results['metrics'] = metrics
            
            # Generate detailed analysis
            summary_metrics, detailed_df = metrics_calculator.generate_detailed_analysis(
                search_results, test_suite
            )
            results['detailed_analysis'] = detailed_df
            
            # Category analysis
            category_analysis = metrics_calculator.analyze_performance_by_category(detailed_df)
            results['category_analysis'] = category_analysis
            
            # Print summary
            print("📈 Performance Summary:")
            for metric_name, metric_value in metrics.items():
                if isinstance(metric_value, (int, float)):
                    if 'Rate' in metric_name:
                        print(f"   {metric_name}: {metric_value:.1%}")
                    else:
                        print(f"   {metric_name}: {metric_value:.3f}")
            
            # Step 6: Generate visualizations and reports
            if self.config['output']['generate_visualizations']:
                print("\n📊 STEP 6: Generating visualizations and reports")
                print("-" * 40)
                
                visualizer = BenchmarkVisualizer(str(self.reports_dir))
                
                # Create charts
                visualizer.create_metrics_overview(metrics)
                visualizer.create_detailed_analysis_chart(detailed_df)
                visualizer.create_performance_radar(metrics)
                
                if category_analysis:
                    visualizer.create_category_performance_chart(category_analysis)
                
                # Generate HTML report
                visualizer.generate_html_report(results)
            
            # Memory cleanup
            memory_stats = embedding_manager.get_memory_stats()
            results['final_memory_stats'] = memory_stats
            embedding_manager.cleanup()
            
            # Benchmark completion
            total_time = time.time() - benchmark_start
            results['benchmark_info']['end_time'] = datetime.now().isoformat()
            results['benchmark_info']['total_time_seconds'] = total_time
            
            print(f"\n🎉 BENCHMARK COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"⏱️  Total time: {total_time:.2f}s")
            print(f"🎯 Overall MRR: {metrics.get('MRR', 0):.3f}")
            print(f"📊 Hit Rate@5: {metrics.get('Hit_Rate@5', 0):.1%}")
            print(f"💾 Reports saved in: {self.reports_dir.absolute()}")
            
            return results
            
        except Exception as e:
            print(f"\n❌ BENCHMARK FAILED: {e}")
            print(traceback.format_exc())
            
            results['benchmark_info']['error'] = str(e)
            results['benchmark_info']['end_time'] = datetime.now().isoformat()
            
            return results
    
    def save_results(self, results: dict) -> None:
        """Save benchmark results to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_path = self.reports_dir / f"benchmark_results_{timestamp}.json"
        
        try:
            # Convert DataFrame to dict for JSON serialization
            if 'detailed_analysis' in results and isinstance(results['detailed_analysis'], pd.DataFrame):
                results['detailed_analysis'] = results['detailed_analysis'].to_dict('records')
            
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Detailed results saved: {results_path}")
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Vietnamese Embedding Model Benchmark Tool')
    parser.add_argument('--config', default='configs/model_config.json', 
                       help='Path to configuration file')
    parser.add_argument('--verbose', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Verify required files exist
    required_files = [
        args.config,
        'data/content.md', 
        'data/test_suite.json'
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Required file not found: {file_path}")
            return 1
    
    try:
        # Run benchmark
        benchmark = Qwen3Benchmark(args.config)
        results = benchmark.run_benchmark()
        
        # Save results
        benchmark.save_results(results)
        
        # Print final instructions
        print("\n📋 Next Steps:")
        print("1. Open 'reports/benchmark_report.html' in your browser")
        print("2. Review interactive charts in 'reports/charts/' directory")
        print("3. Check detailed results in the JSON files")
        
        return 0 if 'error' not in results['benchmark_info'] else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Benchmark interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit(main())
```

## 📄 setup.py

```python
from setuptools import setup, find_packages

setup(
    name="vietnamese-qwen3-benchmark",
    version="1.0.0",
    description="Benchmark tool for Qwen3-Embedding-0.6B on Vietnamese text",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "sentence-transformers>=2.2.2",
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0", 
        "underthesea>=6.7.0",
        "pyvi>=0.1.1",
        "scikit-learn>=1.3.0",
        "transformers>=4.30.0",
        "accelerate>=0.20.0",
        "plotly>=5.15.0",
        "kaleido>=0.2.1",
        "jinja2>=3.1.0",
        "tqdm"
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "vietnamese-benchmark=benchmark:main",
        ],
    },
)
```

## 📖 README.md

```markdown
# Vietnamese Qwen3 Embedding Benchmark 🇻🇳

Công cụ benchmark chuyên dụng cho model **Qwen/Qwen3-Embedding-0.6B** trên dữ liệu tiếng Việt với tối ưu GPU.

## ✨ Tính năng

- **🎯 Chuyên dụng cho Qwen3**: Tối ưu cho model Qwen/Qwen3-Embedding-0.6B
- **🇻🇳 Tiếng Việt**: Hỗ trợ đầy đủ xử lý văn bản tiếng Việt (pyvi, underthesea)
- **⚡ GPU Acceleration**: Tự động detect và sử dụng GPU/CUDA
- **📊 Metrics đầy đủ**: MRR, Hit Rate@K, MAP, NDCG, Precision, Recall
- **📈 Visualizations**: Interactive charts với Plotly
- **📋 HTML Reports**: Báo cáo HTML chi tiết và professional

## 🚀 Cài đặt

### 1. Clone project
```bash
git clone <your-repo>
cd vietnamese_qwen3_benchmark
```

### 2. Tạo virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Cài đặt GPU support (nếu có)
```bash
# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1  
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## 📊 Cách sử dụng

### Chạy benchmark đơn giản
```bash
python benchmark.py
```

### Với custom config
```bash
python benchmark.py --config configs/model_config.json --verbose
```

### Cấu trúc sau khi chạy
```
vietnamese_qwen3_benchmark/
├── reports/
│   ├── benchmark_report.html          # Báo cáo HTML chính
│   ├── benchmark_results_20241201_143022.json
│   ├── chunks_info.json               # Debug info cho chunks
│   └── charts/
│       ├── metrics_overview.html      # Interactive charts
│       ├── detailed_analysis.html
│       ├── performance_radar.html
│       └── category_performance.html
└── model_cache/                       # Cached models
```

## ⚙️ Configuration

### Tùy chỉnh model trong `configs/model_config.json`:
```json
{
  "model": {
    "name": "Qwen/Qwen3-Embedding-0.6B",  // ← Thay đổi model ở đây
    "device": "auto",
    "batch_size": 32,
    "max_seq_length": 512,
    "normalize_embeddings": true
  }
}
```

### Thay đổi dữ liệu test:
- **Content**: Chỉnh sửa `data/content.md`
- **Questions**: Cập nhật `data/test_suite.json`

## 📈 Metrics được đánh giá

| Metric | Mô tả | Mục tiêu |
|--------|-------|----------|
| **MRR** | Mean Reciprocal Rank | > 0.65 |
| **Hit Rate@1** | Top-1 accuracy | > 50% |
| **Hit Rate@5** | Top-5 accuracy | > 75% |
| **Precision@5** | Precision at 5 | > 0.6 |
| **NDCG@5** | Ranking quality | > 0.6 |
| **MAP@5** | Mean Average Precision | > 0.5 |

## 🎯 Kết quả mẫu

```
🎉 BENCHMARK COMPLETED SUCCESSFULLY!
============================================================
⏱️  Total time: 45.23s
🎯 Overall MRR: 0.724
📊 Hit Rate@5: 81.2%
💾 Reports saved in: /path/to/reports
```

## 🔧 Troubleshooting

### CUDA Out of Memory
```bash
# Giảm batch size trong config
"batch_size": 16  # hoặc 8
```

### Model không tải được
```bash
# Xóa cache và thử lại
rm -rf model_cache/
python benchmark.py
```

### Lỗi Vietnamese NLP
```bash
pip uninstall underthesea pyvi
pip install underthesea pyvi
```

## 📊 Hiểu kết quả

### Performance Levels:
- **Excellent** (MRR ≥ 0.7): Sẵn sàng production
- **Good** (MRR ≥ 0.5): Có thể sử dụng với optimizations
- **Average** (MRR ≥ 0.3): Cần fine-tuning
- **Poor** (MRR < 0.3): Cần đổi model hoặc cải thiện data

### Phân tích Category:
- Kiểm tra category nào có hiệu suất thấp nhất
- Xem câu hỏi nào khó nhất (không tìm thấy trong top-5)
- Phân tích score gap giữa top-1 và correct answer

## 🔄 Workflow tùy chỉnh

### Thay đổi model
```bash
# Chỉnh sửa configs/model_config.json
{
  "model": {
    "name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  }
}
```

### Thêm dữ liệu mới
```bash
# 1. Cập nhật data/content.md với nội dung mới
# 2. Tạo câu hỏi tương ứng trong data/test_suite.json
# 3. Chạy benchmark
python benchmark.py
```

### Batch processing nhiều models
```bash
# Tạo script để test nhiều models
for model in "Qwen/Qwen3-Embedding-0.6B" "sentence-transformers/LaBSE"
do
    echo "Testing $model"
    # Update config and run
    python benchmark.py --config configs/${model//\//_}.json
done
```

## 🎛️ Advanced Usage

### Memory optimization
```python
# Trong embedding_manager.py, tùy chỉnh:
def _get_optimal_batch_size(self, requested_batch_size: int) -> int:
    if self.device == "cuda":
        available_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        if available_memory < 4:
            return 8    # Giảm cho GPU nhỏ
        elif available_memory >= 16:
            return 128  # Tăng cho GPU lớn
```

### Custom metrics
```python
# Trong src/metrics.py, thêm metric mới:
def calculate_custom_metric(self, search_results, ground_truth):
    # Custom logic here
    return custom_score
```

## 📝 Logs và Debug

### Enable verbose logging
```bash
python benchmark.py --verbose
```

### Debug chunks
```bash
# Xem chunks_info.json để hiểu cách text được chia
cat reports/chunks_info.json | jq '.chunks[0]'
```

### Memory monitoring
```bash
# Theo dõi GPU memory trong quá trình chạy
watch -n 1 nvidia-smi
```

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/new-feature`
3. Test với Vietnamese data
4. Commit: `git commit -m 'Add Vietnamese feature'`
5. Push: `git push origin feature/new-feature`
6. Tạo Pull Request

## 📄 License

MIT License - xem LICENSE file.

## 🙏 Credits

- [Qwen Team](https://github.com/QwenLM/Qwen) - Qwen3-Embedding model
- [Sentence Transformers](https://www.sbert.net/) - Embedding framework
- [underthesea](https://github.com/undertheseanlp/underthesea) - Vietnamese NLP
- [pyvi](https://github.com/trungtv/pyvi) - Vietnamese tokenization

---

**Happy Benchmarking! 🚀**

Nếu gặp vấn đề, tạo issue trong repository hoặc liên hệ qua email.
```

## 🎯 Hướng dẫn chạy nhanh:

### 1. Cài đặt cơ bản:
```bash
# Clone và setup
git clone <repo>
cd vietnamese_qwen3_benchmark

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Chạy benchmark:
```bash
python benchmark.py
```

### 3. Xem kết quả:
- Mở `reports/benchmark_report.html` trong browser
- Xem các charts interactive trong `reports/charts/`
- Kiểm tra JSON results cho detailed data

## 🔧 Điều chỉnh model:

Để thay đổi model, chỉnh sửa `configs/model_config.json`:
```json
{
  "model": {
    "name": "your-model-name-here",  // ← Thay đổi tại đây
    "device": "auto",
    "batch_size": 32
  }
}
```

## 📊 Output Structure:

Sau khi chạy xong, bạn sẽ có:

1. **HTML Report**: `reports/benchmark_report.html` - Báo cáo tổng quan
2. **Interactive Charts**: `reports/charts/` - Các biểu đồ interactive
3. **JSON Results**: `reports/benchmark_results_*.json` - Dữ liệu chi tiết
4. **Debug Info**: `reports/chunks_info.json` - Thông tin chunks

## 🎯 Expected Performance:

Với Qwen3-Embedding-0.6B trên Vietnamese data:
- **MRR**: 0.65-0.75 (good range)  
- **Hit Rate@5**: 75-85%
- **Processing Speed**: 50-100 texts/second (GPU)
- **Memory Usage**: ~2-4GB GPU RAM

Project này được tối ưu hóa đặc biệt cho Vietnamese text processing và Qwen3 model, với GPU acceleration và comprehensive metrics để đánh giá performance một cách chính xác nhất.
