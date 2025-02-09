export interface Benefit {
  benefit_name: string;
  count?: number;
}

export interface Ingredient {
  ingredient_name: string;
  ingredient_url: string;
  ingredient_uses: string | null;
  ingredient_information: string;
}

export interface ProductData {
  product: string;
  brand: string;
  benefits?: Benefit[];
  notable_ingredients?: string[];
  ingredients_overview: Ingredient[];
  description?: string;
  image_url?: string;
  concerns?: string[];
  product_type?: string;
}

export interface ChatMessage {
  message: string | React.ReactNode;
  isUser: boolean;
  timestamp: string;
}

export interface SearchResult {
  brand: string;
  product: string;
  slug: string;
}

export interface Message {
  id: string;
  content: string | React.ReactNode;
  isUser: boolean;
  timestamp: string;
  isLoading?: boolean;
}

export interface ProductPreview {
  slug: string;
  name: string;
  imageUrl: string;
}
