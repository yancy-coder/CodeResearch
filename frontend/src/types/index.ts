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
