export function HeroSection() {
  return (
    <div
      className="relative h-[600px] bg-cover bg-center"
      style={{
        backgroundImage: `url(https://westcoastuniversity.edu/wp-content/uploads/2023/03/Study-Buddy-Efficiency-Expert-blog.jpg)`,
      }}
    >
      <div className="absolute inset-0 bg-black bg-opacity-50" />
      <div className="absolute inset-0 flex flex-col items-center justify-center text-white pt-20">
        <h1 className="mb-4 text-5xl font-bold">Learn something new everyday.</h1>
        <p className="mb-8 text-xl">Become professionals and ready to join the world.</p>
      </div>
    </div>
  )
}

