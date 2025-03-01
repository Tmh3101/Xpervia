interface DescriptionProps {
    title: string
    description: string
  }
  
  export function Description({ title, description }: DescriptionProps) {
    return (
      <div className="bg-white rounded-xl">
        <h1 className="text-2xl text-destructive font-bold mb-2">{title}</h1>
        <div className="prose max-w-none">
          {description.split("\n").map((paragraph, index) => (
            <p key={index} className="mb-2 text-gray-600 leading-relaxed text-justify">
              {paragraph}
            </p>
          ))}
        </div>
      </div>
    )
  }
  
  