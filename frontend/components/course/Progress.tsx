export const Progress = ({ progress } : { progress: number }) => {
    return (
        <div className="relative w-10 h-10">
            {/* Circular progress bar */}
            <svg className="w-full h-full" viewBox="0 0 100 100">
                {/* Background circle */}
                <circle
                    className="text-gray-200"
                    strokeWidth="8"
                    stroke="currentColor"
                    fill="transparent"
                    r="40"
                    cx="50"
                    cy="50"
                />
                {/* Progress circle */}
                <circle
                    className="text-primary"
                    strokeWidth="8"
                    strokeLinecap="round"
                    stroke="currentColor"
                    fill="transparent"
                    r="40"
                    cx="50"
                    cy="50"
                    strokeDasharray={`${2 * Math.PI * 40}`}
                    strokeDashoffset={`${2 * Math.PI * 40 * (1 - (progress || 0) / 100)}`}
                    transform="rotate(-90 50 50)"
                />
            </svg>
            {/* Percentage text */}
            <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-[10px] text-primary font-medium">{progress || 0}%</span>
            </div>
        </div>
    )
}