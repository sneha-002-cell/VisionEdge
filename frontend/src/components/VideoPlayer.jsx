function VideoPlayer() {
  return (
    <div className="bg-slate-900 rounded-2xl p-4 shadow-xl">

      <h2 className="text-2xl font-semibold mb-4 text-white">
        🎥 Live Camera Feed
      </h2>

      <img
        src="http://127.0.0.1:8000/video"
        alt="Live Stream"
        className="rounded-xl w-full"
      />

    </div>
  );
}

export default VideoPlayer;