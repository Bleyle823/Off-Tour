/**
 * Text-to-video for proposal B-roll when you have no hero still.
 *
 * Usage:
 *   npm run text-to-video -- --prompt "Wide shot of Nairobi skyline with national park grasslands in foreground, morning mist, documentary"
 */
import RunwayML, { TaskFailedError } from "@runwayml/sdk";

function parseArgs(argv) {
  const out = {
    prompt: "",
    model: "gen4.5",
    ratio: "1280:720",
    duration: 5,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--prompt" && argv[i + 1]) out.prompt = argv[++i];
    else if (a === "--model" && argv[i + 1]) out.model = argv[++i];
    else if (a === "--ratio" && argv[i + 1]) out.ratio = argv[++i];
    else if (a === "--duration" && argv[i + 1]) out.duration = Number(argv[++i]);
    else if (a === "--help" || a === "-h") out.help = true;
  }
  return out;
}

function usage() {
  console.log(`Usage: npm run text-to-video -- --prompt "<description>" [--model gen4.5] [--ratio 1280:720] [--duration 5]
`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || !args.prompt) {
    usage();
    process.exit(args.help ? 0 : 1);
  }

  if (!process.env.RUNWAYML_API_SECRET) {
    console.error(
      "RUNWAYML_API_SECRET is not set. Copy scripts/runway/.env.example to scripts/runway/.env and add your key from https://dev.runway.com"
    );
    process.exit(1);
  }

  const client = new RunwayML();

  try {
    const task = await client.textToVideo
      .create({
        model: args.model,
        promptText: args.prompt,
        ratio: args.ratio,
        duration: args.duration,
      })
      .waitForTaskOutput();

    console.log("Task succeeded.");
    console.log("Output URL (temporary — download soon):", task.output?.[0] ?? task.output);
  } catch (error) {
    if (error instanceof TaskFailedError) {
      console.error("Generation failed:", error.taskDetails);
      process.exit(1);
    }
    throw error;
  }
}

main();
