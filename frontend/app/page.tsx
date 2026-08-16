"use client";

import {
  ChangeEvent,
  useEffect,
  useRef,
  useState
} from "react";


type ReceptionResult = {
  status: "needs_input" | "completed" | "error";
  message?: string;
  response_language?: "hi" | "en";
  doctor?: string;
  department?: string;
  appointment_date?: string;
  appointment_time?: string;
};


const API_URL =
  "http://127.0.0.1:8000/reception";


export default function Home() {
  const [sessionId, setSessionId] =
    useState("");

  const [status, setStatus] = useState<
    "idle" |
    "recording" |
    "processing" |
    "done" |
    "error"
  >("idle");

  const [result, setResult] =
    useState<ReceptionResult | null>(null);

  const [seconds, setSeconds] =
    useState(0);

  const inputRef =
    useRef<HTMLInputElement>(null);

  const recorderRef =
    useRef<MediaRecorder | null>(null);

  const streamRef =
    useRef<MediaStream | null>(null);

  const chunksRef =
    useRef<Blob[]>([]);


  /*
   * Create a conversation session when
   * the interface opens.
   */
  useEffect(() => {
    setSessionId(
      crypto.randomUUID()
    );
  }, []);


  /*
   * Recording timer.
   */
  useEffect(() => {
    if (status !== "recording") {
      return;
    }

    const timer = window.setInterval(
      () => {
        setSeconds(
          (value) => value + 1
        );
      },
      1000
    );

    return () => {
      window.clearInterval(timer);
    };
  }, [status]);


  /*
   * Speak the receptionist response using
   * the patient's conversation language.
   */
  function speakMessage(
    message?: string,
    languageCode: "hi" | "en" = "en"
  ) {
    if (
      !message ||
      !("speechSynthesis" in window)
    ) {
      return;
    }

    window.speechSynthesis.cancel();

    const speech =
      new SpeechSynthesisUtterance(
        message
      );

    const browserLanguage =
      languageCode === "hi"
        ? "hi-IN"
        : "en-IN";

    speech.lang = browserLanguage;
    speech.rate = 0.92;
    speech.pitch = 1;
    speech.volume = 1;

    const voices =
      window.speechSynthesis.getVoices();

    const matchingVoice = voices.find(
      (voice) =>
        voice.lang === browserLanguage ||
        voice.lang.startsWith(
          browserLanguage
        )
    );

    if (matchingVoice) {
      speech.voice = matchingVoice;
    }

    window.speechSynthesis.speak(
      speech
    );
  }


  /*
   * Send recorded or uploaded audio
   * to FastAPI.
   */
  async function sendAudio(file: File) {
    setStatus("processing");
    setResult(null);

    const body = new FormData();

    body.append(
      "audio",
      file
    );

    try {
      const response = await fetch(
        `${API_URL}?session_id=${encodeURIComponent(
          sessionId
        )}`,
        {
          method: "POST",
          body
        }
      );

      const data = (await response.json()) as ReceptionResult;

      setResult(data);

      if (
        data.status === "error" ||
        !response.ok
      ) {
        setStatus("error");
      } else {
        setStatus("done");
      }

      speakMessage(
        data.message,
        data.response_language || "en"
      );

    } catch (error) {
      console.error(
        "Receptionist API error:",
        error
      );

      const errorMessage =
        "I cannot reach the receptionist service. " +
        "Please check that FastAPI is running.";

      setResult({
        status: "error",
        message: errorMessage,
        response_language: "en"
      });

      setStatus("error");

      speakMessage(
        errorMessage,
        "en"
      );
    }
  }


  /*
   * Start or stop microphone recording.
   */
  async function toggleRecording() {
    if (status === "recording") {
      recorderRef.current?.stop();
      return;
    }

    try {
      /*
       * Stop the receptionist before the
       * patient begins speaking.
       */
      window.speechSynthesis.cancel();

      const stream =
        await navigator.mediaDevices
          .getUserMedia({
            audio: true
          });

      streamRef.current = stream;
      chunksRef.current = [];

      setSeconds(0);
      setResult(null);

      const recorder =
        new MediaRecorder(stream);

      recorderRef.current = recorder;

      recorder.ondataavailable = (
        event
      ) => {
        if (event.data.size > 0) {
          chunksRef.current.push(
            event.data
          );
        }
      };

      recorder.onstop = () => {
        streamRef.current
          ?.getTracks()
          .forEach(
            (track) => track.stop()
          );

        const audioType =
          recorder.mimeType ||
          "audio/webm";

        const blob = new Blob(
          chunksRef.current,
          {
            type: audioType
          }
        );

        const file = new File(
          [blob],
          `voice-${Date.now()}.webm`,
          {
            type: audioType
          }
        );

        void sendAudio(file);
      };

      recorder.start();

      setStatus("recording");

    } catch (error) {
      console.error(
        "Microphone error:",
        error
      );

      const errorMessage =
        "Microphone access was not available. " +
        "You can upload an audio file instead.";

      setResult({
        status: "error",
        message: errorMessage,
        response_language: "en"
      });

      setStatus("error");

      speakMessage(
        errorMessage,
        "en"
      );
    }
  }


  /*
   * Process an uploaded audio file.
   */
  function handleUpload(
    event: ChangeEvent<HTMLInputElement>
  ) {
    const file =
      event.target.files?.[0];

    if (file) {
      void sendAudio(file);
    }

    event.target.value = "";
  }


  /*
   * Start a new patient conversation.
   */
  function resetConversation() {
    streamRef.current
      ?.getTracks()
      .forEach(
        (track) => track.stop()
      );

    if (
      recorderRef.current &&
      recorderRef.current.state !==
        "inactive"
    ) {
      recorderRef.current.stop();
    }

    window.speechSynthesis.cancel();

    setSessionId(
      crypto.randomUUID()
    );

    setStatus("idle");
    setResult(null);
    setSeconds(0);
  }


  const statusCopy = {
    idle:
      "Tap to speak",

    recording:
      `Listening · ${seconds}s`,

    processing:
      "Processing…",

    done:
      result?.status === "needs_input"
        ? "Waiting for your response"
        : "Appointment confirmed",

    error:
      "Please try again"

  }[status];


  return (
    <main className="shell">
      <div
        className="ambient ambientOne"
      />

      <div
        className="ambient ambientTwo"
      />


      <section
        className="experience"
        aria-live="polite"
      >
        {/* MediTalk logo */}
        <div className="logoWrap">
          <img
            src="/meditalk-logo.png"
            alt="MediTalk"
            className="meditalkLogo"
          />
        </div>


        {/* Alexa-style voice orb */}
        <button
          className={`orb ${status}`}
          onClick={toggleRecording}
          disabled={
            status === "processing"
          }
          aria-label={
            status === "recording"
              ? "Stop recording"
              : "Start recording"
          }
        >
          <span className="orbGlow" />

          <span className="micIcon">
            {status === "recording"
              ? "■"
              : "●"}
          </span>
        </button>


        <p className="statusText">
          {statusCopy}
        </p>


        {/* Follow-up or confirmation */}
        {result?.message && (
          <article
            className={
              `responseCard ${result.status}`
            }
          >
            <span className="responseLabel">
              {result.status === "error"
                ? "Please try again"
                : result.status ===
                    "completed"
                  ? "Confirmed"
                  : "MediTalk"}
            </span>

            <p>
              {result.message}
            </p>


            {result.status ===
              "completed" &&
              result.doctor && (
                <div className="appointmentDetails">
                  <span>
                    {result.doctor}
                  </span>

                  <span>
                    {result.department}
                  </span>

                  <span>
                    {
                      result.appointment_date
                    }
                    {" · "}
                    {
                      result.appointment_time
                    }
                  </span>
                </div>
              )}
          </article>
        )}


        {/* Demo controls */}
        <div className="actions">
          <input
            ref={inputRef}
            type="file"
            accept="audio/*,.m4a"
            onChange={handleUpload}
            hidden
          />

          <button
            className="secondary"
            onClick={() =>
              inputRef.current?.click()
            }
            disabled={
              status === "processing" ||
              status === "recording"
            }
          >
            <span>↑</span>
            Upload audio
          </button>

          <button
            className="secondary"
            onClick={resetConversation}
          >
            <span>↻</span>
            Reset
          </button>
        </div>
      </section>
    </main>
  );
}