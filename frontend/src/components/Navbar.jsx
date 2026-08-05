import { FaVideo } from "react-icons/fa";

function Navbar() {
  return (
    <nav className="bg-slate-900 px-8 py-5 flex justify-between items-center shadow-xl">

      <div className="flex items-center gap-3">

        <FaVideo className="text-blue-400 text-3xl"/>

        <h1 className="text-3xl font-bold text-white">
          VisionEdge AI
        </h1>

      </div>

      <div className="text-green-400 font-bold text-xl animate-pulse">
        ● LIVE
      </div>

    </nav>
  );
}

export default Navbar;