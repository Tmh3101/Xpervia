const ChatLauncher: React.FC<{ open: boolean; onToggle: () => void }> = ({ open, onToggle }) => {
  return (
    <button
      aria-label="Mở chat trợ lý"
      title="Mở chat trợ lý"
      onClick={onToggle}
      className="fixed right-4 bottom-4 z-[9999] inline-flex items-center justify-center w-14 h-14 rounded-full bg-primary text-white shadow-xl hover:scale-105 focus:outline-none focus-visible:ring-4 focus-visible:ring-primary/50"
    >
      <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
        {open ? (
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        ) : (
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 12c0 4.418-4.03 8-9 8a9.97 9.97 0 01-5-1.2L3 20l1.2-4.1A9.97 9.97 0 013 12C3 7.582 7.03 4 12 4s9 3.582 9 8z" />
        )}
      </svg>
    </button>
  );
};

export default ChatLauncher;