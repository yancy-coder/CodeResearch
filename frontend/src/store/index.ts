import { create } from 'zustand';
import type { Code, Category, TextSegment } from '../types';

interface AppState {
  // Data
  codes: Code[];
  categories: Category[];
  segments: TextSegment[];
  
  // Loading state
  isLoading: boolean;
  error: string | null;
  
  // Actions
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
