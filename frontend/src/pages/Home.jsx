import Navbar from "../components/layout/Navbar";
import UploadBox from "../components/upload/UploadBox";

export default function Home() {
  return (
    <>
      <Navbar />

      {/* Hero Section */}
      <section className="max-w-6xl mx-auto px-6 py-20 text-center">
        <h1 className="text-4xl font-bold leading-tight">
          AI-Powered Video Content Moderation
        </h1>

        <p className="mt-6 text-gray-600 max-w-2xl mx-auto">
          Upload your video and instantly detect sexually explicit content,
          hate speech, and violent scenes with timestamp-level precision.
        </p>
      </section>

      {/* Upload Section */}
      <section className="max-w-3xl mx-auto px-6">
        <UploadBox />
      </section>

        <p className="text-green-600 font-bold"> Tailwind is working </p>

      {/* How it works */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <h2 className="text-2xl font-bold text-center mb-12">
          How It Works
        </h2>

        <div className="grid md:grid-cols-3 gap-8 text-center">
          <div>
            <h3 className="font-semibold text-lg">1. Upload Video</h3>
            <p className="text-gray-600 mt-2">
              Upload a short video clip for analysis.
            </p>
          </div>

          <div>
            <h3 className="font-semibold text-lg">2. AI Analysis</h3>
            <p className="text-gray-600 mt-2">
              Our model scans frames and audio for unsafe content.
            </p>
          </div>

          <div>
            <h3 className="font-semibold text-lg">3. Get Insights</h3>
            <p className="text-gray-600 mt-2">
              View confidence scores and exact timestamps.
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
