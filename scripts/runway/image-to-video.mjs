/**
 * Animate a still (local file or HTTPS URL) with Runway image-to-video.
 *
 * Usage:
 *   npm run image-to-video -- --image ../../proposals/images/presentation-murkomen-noordin.jpg --prompt "Slow aerial drift over savannah at golden hour, distant wildlife, documentary tone"
 *
 * Optional: --model gen4.5 --ratio 1280:720 --duration 5 --draft (seedance2_5 preview only; see docs)
 */
import RunwayML, { TaskFailedError } from "@runwayml/sdk";
import { localImageToDataUri } from "./lib/data-uri.mjs";

function parseArgs(argv) {
  const out = {
    image: "",
    prompt:
      "Slow aerial drift over open savannah at golden hour, soft wind in grass, documentary wildlife tone, no close approach to animals",
    model: "gen4.5",
    ratio: "1280:720",
    duration: 5,
    draft: false,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--image" && argv[i + 1]) out.image = argv[++i];
    else if (a === "--prompt" && argv[i + 1]) out.prompt = argv[++i];
    else if (a === "--model" && argv[i + 1]) out.model = argv[++i];
    else if (a === "--ratio" && argv[i + 1]) out.ratio = argv[++i];
    else if (a === "--duration" && argv[i + 1]) out.duration = Number(argv[++i]);
    else if (a === "--draft") out.draft = true;
    else if (a === "--help" || a === "-h") out.help = true;
  }
  return out;
}

function usage() {
  console.log(`Usage: npm run image-to-video -- --image <path-or-https-url> [options]

Options:
  --prompt <text>     Motion / scene description (default: savannah B-roll)
  --model <id>        e.g. gen4.5, gen4_turbo, seedance2_5 (check docs for fields)
  --ratio <w:h>       Model-specific; gen4.5: 1280:720 or 720:1280
  --duration <sec>    Model-specific; gen4.5: 2–10
  --draft             seedance2_5 only: 480p preview before 1080p enhance
`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || !args.image) {
    usage();
    process.exit(args.help ? 0 : 1);
  }

  if (!process.env.RUNWAYML_API_SECRET) {
    console.error(
      "RUNWAYML_API_SECRET is not set. Copy scripts/runway/.env.example to scripts/runway/.env and add your key from https://dev.runway.com"
    );
    process.exit(1);
  }

  const promptImage =
    args.image.startsWith("http://") || args.image.startsWith("https://")
      ? args.image
      : localImageToDataUri(args.image);

  const client = new RunwayML();
  const body = {
    model: args.model,
    promptImage,
    promptText: args.prompt,
    ratio: args.ratio,
    duration: args.duration,
  };
  if (args.draft) body.draft = true;

  try {
    const task = await client.imageToVideo.create(body).waitForTaskOutput();
    const url = task.output?.[0];
    console.log("Task succeeded.");
    console.log("Output URL (temporary — download soon):", url ?? task.output);
    if (args.draft && task.id) {
      console.log("\nDraft task id (for seedance2_5 enhance):", task.id);
    }
  } catch (error) {
    if (error instanceof TaskFailedError) {
      console.error("Generation failed:", error.taskDetails);
      process.exit(1);
    }
    throw error;
  }
}

main();
