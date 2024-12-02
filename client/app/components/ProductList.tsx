interface Product {
  product: string;
  brand: string;
  image_url: string;
}

interface ProductListProps {
  products: Product[];
  onProductSelect: (product: Product) => void;
}

export function ProductList({ products, onProductSelect }: ProductListProps) {
  if (products.length === 0) {
    return null;
  }

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-semibold mb-4 text-[#a984b2]">Search Results</h2>
      <div className="space-y-4">
        {products.map((product, index) => (
          <div 
            key={index}
            onClick={() => onProductSelect(product)}
            className="bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer flex items-center"
          >
            <div className="w-16 h-16 flex-shrink-0">
              <img 
                src={product.image_url || '/placeholder-product.png'}
                alt={product.product}
                className="w-full h-full object-cover rounded-lg"
                onError={(e) => {
                  e.currentTarget.src = '/placeholder-product.png';
                }}
              />
            </div>
            <div className="ml-4 flex-grow">
              <h3 className="font-semibold text-lg text-[#a984b2]">{product.product}</h3>
              <p className="text-gray-600">Brand: {product.brand}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 