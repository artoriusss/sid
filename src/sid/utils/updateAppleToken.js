const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");
const yaml = require("js-yaml");

function extractAccessKey(url) {
  const keyPrefix = "accessKey=";
  const startIndex = url.indexOf(keyPrefix);
  if (startIndex === -1) {
    return null;
  }
  const keyStart = startIndex + keyPrefix.length;
  const keyEnd = url.indexOf("&", keyStart);
  return url.substring(keyStart, keyEnd === -1 ? url.length : keyEnd);
}

function updateYamlFile(accessKey) {
  const filePath = path.join(__dirname, "../../../.sid/.apikeys.yaml");
  try {
    const fileContent = fs.readFileSync(filePath, "utf8");
    const data = yaml.load(fileContent);

    if (data.AM) {
      data.AM.key = accessKey;
      data.AM.timestamp = Math.floor(new Date().getTime() / 1000);
    } else {
      data.AM = {
        key: accessKey,
        timestamp: Math.floor(new Date().getTime() / 1000),
      };
    }

    const yamlStr = yaml.dump(data);
    fs.writeFileSync(filePath, yamlStr, "utf8");
    console.log("YAML file updated successfully.");
  } catch (e) {
    console.error("Failed to update YAML file:", e);
  }
}

(async () => {
  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      cacheEnabled: false,
    });
    const page = await context.newPage();

    let accessKey = null;

    page.on("request", (request) => {
      const url = request.url();
      if (url.includes("sat-cdn.apple-mapkit.com/tile?")) {
        accessKey = extractAccessKey(url);
      }
    });

    await page.goto("https://satellites.pro/", { waitUntil: "load" });

    await page.mouse.move(400, 400);
    await page.mouse.down();
    await page.mouse.move(500, 500, { steps: 10 });
    await page.mouse.up();

    await page.waitForTimeout(5000);

    if (accessKey) {
      updateYamlFile(accessKey);
    }

    console.log("Page title:", await page.title());

    await context.close();
  } catch (error) {
    console.error("Error occurred:", error);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
})();
