import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const OUT_DIR = path.resolve(__dirname, '..', 'artifacts/contracts');
const ABI_DIR = path.resolve(__dirname, '..', 'abi');
const INDEX_PATH = path.join(ABI_DIR, 'index.ts');

function main(): void {
    console.log('🔧 Generating ABI index...');

    if (!fs.existsSync(ABI_DIR)) {
        fs.mkdirSync(ABI_DIR, { recursive: true });
    }

    // Extract ABI's
    const abiNames: string[] = [];
    const contractFolders = fs.readdirSync(OUT_DIR);
    for (const folder of contractFolders) {
        const folderPath = path.join(OUT_DIR, folder);
        if (!fs.statSync(folderPath).isDirectory()) continue;

        const files = fs.readdirSync(folderPath);
        for (const file of files) {
            if (!file.endsWith('.json')) continue;

            const filePath = path.join(folderPath, file);
            const fileContent = fs.readFileSync(filePath, 'utf-8');
            const parsed = JSON.parse(fileContent);

            if (!parsed.abi) continue;

            const contractName = path.basename(file, '.json');
            const targetPath = path.join(ABI_DIR, `${contractName}.ts`);

            fs.writeFileSync(
                targetPath,
                `export const ${contractName}Abi = ${JSON.stringify(parsed.abi, null, 2)} as const;`
            );
            abiNames.push(contractName);
        }
    }

    // Generate index.ts
    const exports = abiNames.map((name) =>
        `export * from './${name}';`
    );

    const indexContent = exports.join('\n');
    fs.writeFileSync(INDEX_PATH, indexContent, 'utf-8');

    console.log('✅ ABI index generated!');
}

main();