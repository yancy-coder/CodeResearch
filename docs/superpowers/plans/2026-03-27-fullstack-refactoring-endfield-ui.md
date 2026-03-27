# CoderResearch 全栈重构计划 - 终末地风格 UI

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** 将 CoderResearch 重构为 FastAPI 后端 + TypeScript/TailwindCSS 前端，采用终末地游戏 UI 风格

**Architecture:**
- **Backend:** FastAPI + native SQLite (aiosqlite) + Pydantic models
- **Frontend:** TypeScript + React + TailwindCSS + Vite
- **UI Style:** 终末地 (Arknights: Endfield) 风格 - 深色科技风、橙色强调色、几何线条

**Tech Stack:** Python 3.11+, FastAPI, aiosqlite, TypeScript, React 18, TailwindCSS, Vite

---

## 终末地 UI 风格规范

### 色彩系统
```css
/* 主色调 */
--color-bg-primary: #0a0a0f;      /* 深空黑 */
--color-bg-secondary: #12121a;    /* 次级背景 */
--color-bg-card: #1a1a25;         /* 卡片背景 */

/* 强调色 */
--color-accent: #ff6b35;          /* 终末地橙 */
--color-accent-hover: #ff8555;    /* 悬停橙 */
--color-accent-dim: #cc5529;      /* 暗淡橙 */

/* 文字 */
--color-text-primary: #ffffff;
--color-text-secondary: #a0a0b0;
--color-text-muted: #606070;

/* 边框 */
--color-border: #2a2a3a;
--color-border-accent: #ff6b35;
```

### 视觉特征
- **边角:** 2-4px 小圆角，保持科技感
- **线条:** 1px 细边框，几何分割
- **阴影:**  subtle glow 效果 (`0 0 20px rgba(255,107,53,0.1)`)
- **字体:** Inter / Noto Sans SC，等宽数字
- **动画:** 快速过渡 (150-200ms)，线性或 ease-out

---

## Phase 1: FastAPI 后端基础

### Task 1: 项目结构初始化

**Files:**
- Create: `backend/main.py` - FastAPI 入口
- Create: `backend/requirements.txt` - 依赖
- Create: `backend/__init__.py`

**Implementation:**

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import init_db
from routers import codes, categories, sessions, import_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title="CoderResearch API",
    description="质性研究编码系统 API",
    version="3.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(codes.router, prefix="/api/codes", tags=["codes"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(import_data.router, prefix="/api/import", tags=["import"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "3.0.0"}
```

```txt
# backend/requirements.txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
aiosqlite>=0.19.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-multipart>=0.0.6
```

### Testing
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# Test: curl http://localhost:8000/api/health
```

---

### Task 2: SQLite 数据库层 (aiosqlite)

**Files:**
- Create: `backend/database.py` - 数据库连接和初始化
- Create: `backend/models.py` - Pydantic 模型

**Implementation:**

```python
# backend/database.py
import aiosqlite
from contextvars import ContextVar
from typing import Optional

DB_PATH = "coderresearch_v3.db"
db_connection: ContextVar[Optional[aiosqlite.Connection]] = ContextVar("db_connection", default=None)


async def get_db() -> aiosqlite.Connection:
    """获取数据库连接"""
    conn = db_connection.get()
    if conn is None:
        conn = await aiosqlite.connect(DB_PATH)
        conn.row_factory = aiosqlite.Row
        db_connection.set(conn)
    return conn


async def init_db():
    """初始化数据库表"""
    conn = await get_db()
    
    # Codes 表
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS codes (
            id TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            definition TEXT DEFAULT '',
            level TEXT DEFAULT 'open',
            category_id TEXT,
            created_by TEXT DEFAULT 'human',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            version TEXT DEFAULT '1.0'
        )
    """)
    
    # Categories 表
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            definition TEXT DEFAULT '',
            parent_id TEXT,
            properties TEXT DEFAULT '[]',
            dimensions TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Sessions 表
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            data TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Text segments 表
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS segments (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            source TEXT,
            position_start INTEGER,
            position_end INTEGER,
            session_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    await conn.commit()


async def close_db():
    """关闭数据库连接"""
    conn = db_connection.get()
    if conn:
        await conn.close()
        db_connection.set(None)
```

```python
# backend/models.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CodeBase(BaseModel):
    label: str
    definition: str = ""
    level: str = "open"  # open, axial, selective
    category_id: Optional[str] = None


class CodeCreate(CodeBase):
    id: Optional[str] = None
    created_by: str = "human"


class Code(CodeBase):
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    version: str
    
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    definition: str = ""
    parent_id: Optional[str] = None


class CategoryCreate(CategoryBase):
    id: Optional[str] = None


class Category(CategoryBase):
    id: str
    properties: List[str] = []
    dimensions: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


class TextSegment(BaseModel):
    id: str
    content: str
    source: str
    position: tuple[int, int]


class Session(BaseModel):
    id: str
    data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

---

### Task 3: Codes API Router

**Files:**
- Create: `backend/routers/__init__.py`
- Create: `backend/routers/codes.py`

**Implementation:**

```python
# backend/routers/codes.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import uuid
import json

from database import get_db
from models import Code, CodeCreate

router = APIRouter()


@router.get("", response_model=List[Code])
async def list_codes(
    level: Optional[str] = Query(None, description="Filter by level: open, axial, selective")
):
    """获取所有代码"""
    conn = await get_db()
    
    if level:
        cursor = await conn.execute(
            "SELECT * FROM codes WHERE level = ? ORDER BY created_at DESC",
            (level,)
        )
    else:
        cursor = await conn.execute("SELECT * FROM codes ORDER BY created_at DESC")
    
    rows = await cursor.fetchall()
    return [Code(**dict(row)) for row in rows]


@router.get("/{code_id}", response_model=Code)
async def get_code(code_id: str):
    """获取单个代码"""
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM codes WHERE id = ?", (code_id,))
    row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Code not found")
    
    return Code(**dict(row))


@router.post("", response_model=Code)
async def create_code(code: CodeCreate):
    """创建新代码"""
    conn = await get_db()
    code_id = code.id or str(uuid.uuid4())[:8]
    
    await conn.execute(
        """
        INSERT INTO codes (id, label, definition, level, category_id, created_by)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (code_id, code.label, code.definition, code.level, code.category_id, code.created_by)
    )
    await conn.commit()
    
    return await get_code(code_id)


@router.put("/{code_id}", response_model=Code)
async def update_code(code_id: str, code: CodeCreate):
    """更新代码"""
    conn = await get_db()
    
    # Check exists
    cursor = await conn.execute("SELECT id FROM codes WHERE id = ?", (code_id,))
    if not await cursor.fetchone():
        raise HTTPException(status_code=404, detail="Code not found")
    
    await conn.execute(
        """
        UPDATE codes 
        SET label = ?, definition = ?, level = ?, category_id = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (code.label, code.definition, code.level, code.category_id, code_id)
    )
    await conn.commit()
    
    return await get_code(code_id)


@router.delete("/{code_id}")
async def delete_code(code_id: str):
    """删除代码"""
    conn = await get_db()
    
    cursor = await conn.execute("SELECT id FROM codes WHERE id = ?", (code_id,))
    if not await cursor.fetchone():
        raise HTTPException(status_code=404, detail="Code not found")
    
    await conn.execute("DELETE FROM codes WHERE id = ?", (code_id,))
    await conn.commit()
    
    return {"message": "Code deleted", "id": code_id}
```

---

### Task 4: Categories 和 Sessions API

**Files:**
- Create: `backend/routers/categories.py`
- Create: `backend/routers/sessions.py`

**Implementation (categories.py):**

```python
# backend/routers/categories.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import uuid
import json

from database import get_db
from models import Category, CategoryCreate

router = APIRouter()


@router.get("", response_model=List[Category])
async def list_categories(parent_id: Optional[str] = None):
    """获取所有类属"""
    conn = await get_db()
    
    if parent_id is not None:
        cursor = await conn.execute(
            "SELECT * FROM categories WHERE parent_id = ?",
            (parent_id,)
        )
    else:
        cursor = await conn.execute("SELECT * FROM categories")
    
    rows = await cursor.fetchall()
    categories = []
    for row in rows:
        data = dict(row)
        data['properties'] = json.loads(data.get('properties', '[]'))
        data['dimensions'] = json.loads(data.get('dimensions', '{}'))
        categories.append(Category(**data))
    
    return categories


@router.post("", response_model=Category)
async def create_category(category: CategoryCreate):
    """创建类属"""
    conn = await get_db()
    cat_id = str(uuid.uuid4())[:8]
    
    await conn.execute(
        """
        INSERT INTO categories (id, name, definition, parent_id, properties, dimensions)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (cat_id, category.name, category.definition, category.parent_id, '[]', '{}')
    )
    await conn.commit()
    
    return Category(id=cat_id, **category.model_dump())


@router.get("/{category_id}", response_model=Category)
async def get_category(category_id: str):
    """获取单个类属"""
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
    row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Category not found")
    
    data = dict(row)
    data['properties'] = json.loads(data.get('properties', '[]'))
    data['dimensions'] = json.loads(data.get('dimensions', '{}'))
    return Category(**data)
```

**Implementation (sessions.py):**

```python
# backend/routers/sessions.py
from fastapi import APIRouter, HTTPException
import json

from database import get_db
from models import Session

router = APIRouter()


@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: str = "default"):
    """获取会话"""
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = await cursor.fetchone()
    
    if not row:
        # Create default session
        await conn.execute(
            "INSERT INTO sessions (id, data) VALUES (?, ?)",
            (session_id, '{}')
        )
        await conn.commit()
        return Session(id=session_id, data={}, created_at=None, updated_at=None)
    
    data = dict(row)
    data['data'] = json.loads(data.get('data', '{}'))
    return Session(**data)


@router.put("/{session_id}")
async def update_session(session_id: str, data: dict):
    """更新会话"""
    conn = await get_db()
    
    await conn.execute(
        """
        INSERT INTO sessions (id, data, updated_at) 
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET 
            data = excluded.data,
            updated_at = CURRENT_TIMESTAMP
        """,
        (session_id, json.dumps(data))
    )
    await conn.commit()
    
    return {"message": "Session updated", "id": session_id}
```

---

### Task 5: Import API

**Files:**
- Create: `backend/routers/import_data.py`

**Implementation:**

```python
# backend/routers/import_data.py
from fastapi import APIRouter, UploadFile, File
from typing import List
import uuid
import re

from database import get_db
from models import TextSegment

router = APIRouter()


@router.post("/text")
async def import_text(
    file: UploadFile = File(...),
    segment_type: str = "paragraph"
):
    """导入文本文件"""
    content = await file.read()
    text = content.decode('utf-8')
    
    # Parse segments
    if segment_type == "paragraph":
        raw_segments = [s.strip() for s in text.split('\n\n') if s.strip()]
    else:
        raw_segments = [s.strip() for s in text.split('\n') if s.strip()]
    
    segments: List[TextSegment] = []
    position = 0
    
    for seg_text in raw_segments:
        seg_id = f"seg-{uuid.uuid4().hex[:6]}"
        segments.append(TextSegment(
            id=seg_id,
            content=seg_text[:500],  # Limit length
            source=file.filename,
            position=(position, position + len(seg_text))
        ))
        position += len(seg_text) + 2
    
    # Save to database
    conn = await get_db()
    for seg in segments:
        await conn.execute(
            """
            INSERT INTO segments (id, content, source, position_start, position_end)
            VALUES (?, ?, ?, ?, ?)
            """,
            (seg.id, seg.content, seg.source, seg.position[0], seg.position[1])
        )
    await conn.commit()
    
    return {
        "message": f"Imported {len(segments)} segments",
        "segments": segments
    }


@router.get("/segments")
async def list_segments():
    """获取所有文本片段"""
    conn = await get_db()
    cursor = await conn.execute("SELECT * FROM segments ORDER BY created_at DESC")
    rows = await cursor.fetchall()
    
    segments = []
    for row in rows:
        data = dict(row)
        segments.append(TextSegment(
            id=data['id'],
            content=data['content'],
            source=data['source'],
            position=(data['position_start'], data['position_end'])
        ))
    
    return segments
```

---

## Phase 2: 前端基础

### Task 6: Vite + React + TypeScript 初始化

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`

**Commands:**
```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm install tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**Configuration:**

```json
// frontend/package.json
{
  "name": "coderresearch-frontend",
  "private": true,
  "version": "3.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "zustand": "^4.4.0",
    "@tanstack/react-query": "^5.0.0",
    "axios": "^1.6.0",
    "lucide-react": "^0.294.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.3.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

```typescript
// frontend/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

---

### Task 7: Tailwind 终末地主题配置

**Files:**
- Create: `frontend/tailwind.config.js`
- Create: `frontend/src/index.css`

**Implementation:**

```javascript
// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 终末地色彩系统
        endfield: {
          bg: {
            primary: '#0a0a0f',
            secondary: '#12121a',
            card: '#1a1a25',
            hover: '#222230'
          },
          accent: {
            DEFAULT: '#ff6b35',
            hover: '#ff8555',
            dim: '#cc5529',
            glow: 'rgba(255, 107, 53, 0.3)'
          },
          border: {
            DEFAULT: '#2a2a3a',
            accent: '#ff6b35'
          },
          text: {
            primary: '#ffffff',
            secondary: '#a0a0b0',
            muted: '#606070'
          }
        }
      },
      fontFamily: {
        sans: ['Inter', 'Noto Sans SC', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate'
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(255, 107, 53, 0.2)' },
          '100%': { boxShadow: '0 0 20px rgba(255, 107, 53, 0.4)' }
        }
      }
    },
  },
  plugins: [],
}
```

```css
/* frontend/src/index.css */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  * {
    @apply border-endfield-border;
  }
  
  body {
    @apply bg-endfield-bg-primary text-endfield-text-primary font-sans antialiased;
  }
  
  /* 滚动条样式 */
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  
  ::-webkit-scrollbar-track {
    @apply bg-endfield-bg-secondary;
  }
  
  ::-webkit-scrollbar-thumb {
    @apply bg-endfield-border rounded-full;
  }
  
  ::-webkit-scrollbar-thumb:hover {
    @apply bg-endfield-text-muted;
  }
}

@layer components {
  /* 终末地风格卡片 */
  .ef-card {
    @apply bg-endfield-bg-card border border-endfield-border rounded-lg;
    @apply hover:border-endfield-accent/50 transition-all duration-200;
  }
  
  /* 终末地风格按钮 */
  .ef-btn {
    @apply px-4 py-2 rounded-md font-medium transition-all duration-150;
    @apply focus:outline-none focus:ring-2 focus:ring-endfield-accent/50;
  }
  
  .ef-btn-primary {
    @apply ef-btn bg-endfield-accent text-white;
    @apply hover:bg-endfield-accent-hover;
  }
  
  .ef-btn-secondary {
    @apply ef-btn bg-endfield-bg-secondary text-endfield-text-secondary;
    @apply hover:bg-endfield-bg-hover hover:text-endfield-text-primary;
  }
  
  /* 终末地风格输入框 */
  .ef-input {
    @apply w-full px-4 py-2 bg-endfield-bg-secondary border border-endfield-border rounded-md;
    @apply text-endfield-text-primary placeholder-endfield-text-muted;
    @apply focus:outline-none focus:border-endfield-accent focus:ring-1 focus:ring-endfield-accent;
  }
  
  /* 科技分割线 */
  .ef-divider {
    @apply h-px bg-gradient-to-r from-transparent via-endfield-border to-transparent;
  }
  
  /* 状态标签 */
  .ef-badge {
    @apply px-2 py-0.5 text-xs font-mono rounded border;
  }
  
  .ef-badge-accent {
    @apply ef-badge bg-endfield-accent/10 border-endfield-accent text-endfield-accent;
  }
}
```

---

## Phase 3: 前端核心组件

### Task 8: 类型定义和 API 客户端

**Files:**
- Create: `frontend/src/types/index.ts`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/store/index.ts`

**Implementation:**

```typescript
// frontend/src/types/index.ts
export interface Code {
  id: string;
  label: string;
  definition: string;
  level: 'open' | 'axial' | 'selective';
  category_id?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  version: string;
}

export interface Category {
  id: string;
  name: string;
  definition: string;
  parent_id?: string;
  properties: string[];
  dimensions: Record<string, any>;
  created_at: string;
}

export interface TextSegment {
  id: string;
  content: string;
  source: string;
  position: [number, number];
}

export interface Session {
  id: string;
  data: {
    segments?: TextSegment[];
    codes?: Code[];
    categories?: Category[];
  };
  created_at: string;
  updated_at: string;
}
```

```typescript
// frontend/src/api/client.ts
import axios from 'axios';
import type { Code, Category, TextSegment } from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Codes API
export const codesApi = {
  list: (level?: string) => api.get<Code[]>('/codes', { params: { level } }),
  get: (id: string) => api.get<Code>(`/codes/${id}`),
  create: (data: Partial<Code>) => api.post<Code>('/codes', data),
  update: (id: string, data: Partial<Code>) => api.put<Code>(`/codes/${id}`, data),
  delete: (id: string) => api.delete(`/codes/${id}`)
};

// Categories API
export const categoriesApi = {
  list: () => api.get<Category[]>('/categories'),
  get: (id: string) => api.get<Category>(`/categories/${id}`),
  create: (data: Partial<Category>) => api.post<Category>('/categories', data)
};

// Import API
export const importApi = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/import/text', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  listSegments: () => api.get<TextSegment[]>('/import/segments')
};

export default api;
```

```typescript
// frontend/src/store/index.ts
import { create } from 'zustand';
import type { Code, Category, TextSegment } from '../types';

interface AppState {
  // 数据
  codes: Code[];
  categories: Category[];
  segments: TextSegment[];
  
  // 加载状态
  isLoading: boolean;
  error: string | null;
  
  // 操作方法
  setCodes: (codes: Code[]) => void;
  setCategories: (categories: Category[]) => void;
  setSegments: (segments: TextSegment[]) => void;
  addCode: (code: Code) => void;
  removeCode: (id: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useStore = create<AppState>((set) => ({
  codes: [],
  categories: [],
  segments: [],
  isLoading: false,
  error: null,
  
  setCodes: (codes) => set({ codes }),
  setCategories: (categories) => set({ categories }),
  setSegments: (segments) => set({ segments }),
  addCode: (code) => set((state) => ({ codes: [code, ...state.codes] })),
  removeCode: (id) => set((state) => ({ 
    codes: state.codes.filter(c => c.id !== id) 
  })),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error })
}));
```

---

### Task 9: 终末地风格 UI 组件

**Files:**
- Create: `frontend/src/components/Layout.tsx`
- Create: `frontend/src/components/Sidebar.tsx`
- Create: `frontend/src/components/Card.tsx`
- Create: `frontend/src/components/Button.tsx`

**Implementation (Layout.tsx):**

```tsx
// frontend/src/components/Layout.tsx
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function Layout() {
  return (
    <div className="min-h-screen bg-endfield-bg-primary flex">
      <Sidebar />
      <main className="flex-1 p-6 overflow-auto">
        <div className="max-w-7xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
```

**Implementation (Sidebar.tsx):**

```tsx
// frontend/src/components/Sidebar.tsx
import { NavLink } from 'react-router-dom';
import { FileText, Code, FolderTree, Settings, Database } from 'lucide-react';

const navItems = [
  { path: '/', icon: Database, label: '概览' },
  { path: '/import', icon: FileText, label: '导入数据' },
  { path: '/codes', icon: Code, label: '代码本' },
  { path: '/categories', icon: FolderTree, label: '类属' },
  { path: '/settings', icon: Settings, label: '设置' },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-endfield-bg-secondary border-r border-endfield-border flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-endfield-border">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-endfield-accent rounded flex items-center justify-center">
            <span className="text-white font-bold text-sm">CR</span>
          </div>
          <div>
            <h1 className="text-lg font-bold text-endfield-text-primary">CoderResearch</h1>
            <p className="text-xs text-endfield-text-muted">v3.0.0</p>
          </div>
        </div>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `
              flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-150
              ${isActive 
                ? 'bg-endfield-accent/10 text-endfield-accent border border-endfield-accent/30' 
                : 'text-endfield-text-secondary hover:bg-endfield-bg-hover hover:text-endfield-text-primary'
              }
            `}
          >
            <item.icon size={18} />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>
      
      {/* Footer */}
      <div className="p-4 border-t border-endfield-border">
        <div className="ef-card p-3">
          <div className="flex items-center gap-2 text-xs text-endfield-text-muted">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span>系统运行正常</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
```

**Implementation (Card.tsx):**

```tsx
// frontend/src/components/Card.tsx
import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  title?: string;
  className?: string;
  accent?: boolean;
}

export default function Card({ children, title, className = '', accent = false }: CardProps) {
  return (
    <div className={`
      ef-card p-6 ${className}
      ${accent ? 'border-endfield-accent/50 shadow-lg shadow-endfield-accent/5' : ''}
    `}>
      {title && (
        <>
          <h3 className="text-lg font-semibold text-endfield-text-primary mb-4">{title}</h3>
          <div className="ef-divider mb-4" />
        </>
      )}
      {children}
    </div>
  );
}
```

**Implementation (Button.tsx):**

```tsx
// frontend/src/components/Button.tsx
import type { ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

export default function Button({ 
  children, 
  variant = 'primary', 
  size = 'md',
  loading = false,
  disabled,
  className = '',
  ...props 
}: ButtonProps) {
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg'
  };
  
  const variantClasses = {
    primary: 'ef-btn-primary',
    secondary: 'ef-btn-secondary',
    danger: 'ef-btn bg-red-600 text-white hover:bg-red-700'
  };
  
  return (
    <button
      className={`${variantClasses[variant]} ${sizeClasses[size]} ${className} ${
        disabled || loading ? 'opacity-50 cursor-not-allowed' : ''
      }`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          加载中...
        </span>
      ) : children}
    </button>
  );
}
```

---

## Phase 4: 前端页面

### Task 10: 页面组件

**Files:**
- Create: `frontend/src/pages/Overview.tsx`
- Create: `frontend/src/pages/ImportPage.tsx`
- Create: `frontend/src/pages/CodesPage.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/main.tsx`

**Implementation (Overview.tsx):**

```tsx
// frontend/src/pages/Overview.tsx
import { useEffect } from 'react';
import { Code, FolderTree, FileText, Activity } from 'lucide-react';
import Card from '../components/Card';
import { useStore } from '../store';
import { codesApi, categoriesApi, importApi } from '../api/client';

export default function Overview() {
  const { codes, categories, segments, setCodes, setCategories, setSegments } = useStore();
  
  useEffect(() => {
    // Load data
    codesApi.list().then(res => setCodes(res.data));
    categoriesApi.list().then(res => setCategories(res.data));
    importApi.listSegments().then(res => setSegments(res.data));
  }, []);
  
  const stats = [
    { label: '代码数量', value: codes.length, icon: Code, color: 'text-blue-400' },
    { label: '类属数量', value: categories.length, icon: FolderTree, color: 'text-purple-400' },
    { label: '文本片段', value: segments.length, icon: FileText, color: 'text-green-400' },
    { label: '系统状态', value: '正常', icon: Activity, color: 'text-endfield-accent' },
  ];
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-endfield-text-primary mb-2">概览</h2>
        <p className="text-endfield-text-secondary">项目整体状态监控</p>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label} className="flex items-center gap-4">
            <div className={`p-3 rounded-lg bg-endfield-bg-secondary ${stat.color}`}>
              <stat.icon size={24} />
            </div>
            <div>
              <p className="text-2xl font-bold text-endfield-text-primary">{stat.value}</p>
              <p className="text-sm text-endfield-text-muted">{stat.label}</p>
            </div>
          </Card>
        ))}
      </div>
      
      {/* Recent Codes */}
      <Card title="最近代码">
        {codes.length === 0 ? (
          <div className="text-center py-8 text-endfield-text-muted">
            <p>暂无代码，请先导入数据并进行编码</p>
          </div>
        ) : (
          <div className="space-y-2">
            {codes.slice(0, 5).map((code) => (
              <div 
                key={code.id} 
                className="flex items-center justify-between p-3 bg-endfield-bg-secondary rounded-lg"
              >
                <div>
                  <span className="font-medium text-endfield-text-primary">{code.label}</span>
                  <span className="ef-badge-accent ml-2">{code.level}</span>
                </div>
                <span className="text-sm text-endfield-text-muted">{code.created_by}</span>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
```

**Implementation (CodesPage.tsx):**

```tsx
// frontend/src/pages/CodesPage.tsx
import { useEffect, useState } from 'react';
import { Plus, Trash2, Edit } from 'lucide-react';
import Card from '../components/Card';
import Button from '../components/Button';
import { useStore } from '../store';
import { codesApi } from '../api/client';
import type { Code } from '../types';

export default function CodesPage() {
  const { codes, setCodes, removeCode } = useStore();
  const [isCreating, setIsCreating] = useState(false);
  const [newCode, setNewCode] = useState({ label: '', definition: '', level: 'open' as const });
  
  useEffect(() => {
    codesApi.list().then(res => setCodes(res.data));
  }, []);
  
  const handleCreate = async () => {
    if (!newCode.label) return;
    const res = await codesApi.create(newCode);
    setCodes([res.data, ...codes]);
    setIsCreating(false);
    setNewCode({ label: '', definition: '', level: 'open' });
  };
  
  const handleDelete = async (id: string) => {
    await codesApi.delete(id);
    removeCode(id);
  };
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-endfield-text-primary mb-2">代码本</h2>
          <p className="text-endfield-text-secondary">管理质性编码</p>
        </div>
        <Button onClick={() => setIsCreating(true)}>
          <Plus size={18} className="mr-1" />
          新建代码
        </Button>
      </div>
      
      {/* Create Form */}
      {isCreating && (
        <Card accent>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-endfield-text-secondary mb-1">
                代码标签
              </label>
              <input
                type="text"
                className="ef-input"
                value={newCode.label}
                onChange={(e) => setNewCode({ ...newCode, label: e.target.value })}
                placeholder="输入代码标签"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-endfield-text-secondary mb-1">
                定义
              </label>
              <textarea
                className="ef-input h-24 resize-none"
                value={newCode.definition}
                onChange={(e) => setNewCode({ ...newCode, definition: e.target.value })}
                placeholder="输入代码定义"
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleCreate}>保存</Button>
              <Button variant="secondary" onClick={() => setIsCreating(false)}>取消</Button>
            </div>
          </div>
        </Card>
      )}
      
      {/* Codes List */}
      <div className="space-y-3">
        {codes.map((code) => (
          <Card key={code.id} className="group">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-endfield-text-primary">
                    {code.label}
                  </h3>
                  <span className="ef-badge-accent">{code.level}</span>
                  <span className="text-xs text-endfield-text-muted font-mono">#{code.id}</span>
                </div>
                <p className="text-endfield-text-secondary">{code.definition || '暂无定义'}</p>
                <div className="mt-3 flex items-center gap-4 text-sm text-endfield-text-muted">
                  <span>创建者: {code.created_by}</span>
                  <span>版本: {code.version}</span>
                </div>
              </div>
              <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button className="p-2 text-endfield-text-muted hover:text-endfield-accent transition-colors">
                  <Edit size={18} />
                </button>
                <button 
                  className="p-2 text-endfield-text-muted hover:text-red-400 transition-colors"
                  onClick={() => handleDelete(code.id)}
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
```

**Implementation (App.tsx):**

```tsx
// frontend/src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import Overview from './pages/Overview';
import ImportPage from './pages/ImportPage';
import CodesPage from './pages/CodesPage';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Overview />} />
            <Route path="import" element={<ImportPage />} />
            <Route path="codes" element={<CodesPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
```

**Implementation (main.tsx):**

```tsx
// frontend/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

---

## Phase 5: 集成与部署

### Task 11: 启动脚本和文档

**Files:**
- Create: `start.py` - 统一启动脚本
- Modify: `README.md` - 更新文档

**Implementation (start.py):**

```python
#!/usr/bin/env python3
"""CoderResearch 全栈启动脚本"""
import subprocess
import sys
import os


def start_backend():
    """启动 FastAPI 后端"""
    print("🚀 启动后端服务...")
    os.chdir("backend")
    subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"])
    os.chdir("..")


def start_frontend():
    """启动前端开发服务器"""
    print("🎨 启动前端服务...")
    os.chdir("frontend")
    subprocess.Popen(["npm", "run", "dev"])
    os.chdir("..")


if __name__ == "__main__":
    print("=" * 50)
    print("CoderResearch v3.0 - 全栈开发模式")
    print("=" * 50)
    
    start_backend()
    start_frontend()
    
    print("\n✅ 服务已启动:")
    print("   后端: http://localhost:8000")
    print("   前端: http://localhost:5173")
    print("   API 文档: http://localhost:8000/docs")
    print("\n按 Ctrl+C 停止服务")
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n\n🛑 停止服务...")
```

---

## Summary

| Phase | Tasks | 产出 |
|-------|-------|------|
| 1 | 5 | FastAPI 后端 + SQLite |
| 2 | 2 | Vite + TS + Tailwind |
| 3 | 2 | API 客户端 + Store |
| 4 | 1 | 页面组件 |
| 5 | 1 | 集成脚本 |

**总计:** 11 Tasks

### 运行方式

```bash
# 安装依赖
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 启动开发环境
cd .. && python start.py

# 访问
# 前端: http://localhost:5173
# 后端: http://localhost:8000
# API 文档: http://localhost:8000/docs
```
