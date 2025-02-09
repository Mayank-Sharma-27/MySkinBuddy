export interface Ingredient {
  ingredient_name: string;
  ingredient_url: string;
  ingredient_uses: string | null;
  ingredient_information: string;
}

export interface Benefit {
  benefit_name: string;
  count?: number;
}

export interface ProductData {
  brand: string;
  product: string;
  ingredients_overview: Ingredient[];
  benefits: Benefit[];
  concerns: string[];
  notable_ingredients: string[];
}
