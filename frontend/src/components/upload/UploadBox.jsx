export default function UploadBox() {
  return (
    <div className="border-2 border-dashed rounded-xl p-8 text-center hover:border-black transition">
      <input
        type="file"
        accept="video/*"
        className="hidden"
        id="videoUpload"
      />

      <label htmlFor="videoUpload" className="cursor-pointer">
        <p className="text-lg font-semibold">
          Drag & Drop your video here
        </p>
        <p className="text-sm text-gray-500 mt-2">
          or click to browse (MP4, AVI, MKV)
        </p>

        <button className="mt-4 px-6 py-2 bg-black text-white rounded-lg">
          Upload Video
        </button>
      </label>
    </div>
  );
}
