export default function Navbar() {
  return (
    <nav className="w-full px-8 py-4 flex justify-between items-center border-b">
      <h1 className="text-xl font-bold text-gray-800">
        VideoGuard AI
      </h1>

      <div className="space-x-6 text-sm font-medium text-gray-600">
        <a href="#" className="hover:text-black">About</a>
        <a href="#" className="hover:text-black">Docs</a>
        <a href="#" className="hover:text-black">GitHub</a>
      </div>
    </nav>
  );
}
