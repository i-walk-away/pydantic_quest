require('/piston_api/node_modules/nocamel');

const { execFileSync } = require('child_process');
const fs = require('fs');
const Package = require('/piston_api/src/package');

const LANGUAGE = process.env.PISTON_RUNTIME_LANGUAGE || 'python';
const VERSION = process.env.PISTON_RUNTIME_VERSION || '3.12.0';
const MAX_ATTEMPTS = Number(process.env.PISTON_RUNTIME_INSTALL_ATTEMPTS || '3');
const PYDANTIC_SPEC = process.env.PISTON_RUNTIME_PYDANTIC_SPEC || 'pydantic>=2.12,<3';
const RUNTIME_PATH = `/piston/packages/${LANGUAGE}/${VERSION}`;
const PYTHON_BIN = `${RUNTIME_PATH}/bin/python3`;
const RUNTIME_INSTALLED_MARKER = `${RUNTIME_PATH}/.ppman-installed`;

function runtimeInstalled() {
    return fs.existsSync(RUNTIME_INSTALLED_MARKER);
}

async function installRuntime() {
    if (runtimeInstalled()) {
        return;
    }

    for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
        try {
            const pkg = await Package.get_package(LANGUAGE, VERSION);

            if (!pkg) {
                throw new Error(`Runtime package not found: ${LANGUAGE}@${VERSION}`);
            }

            if (!pkg.installed) {
                await pkg.install();
            }

            return;
        } catch (error) {
            if (attempt === MAX_ATTEMPTS) {
                throw error;
            }

            // Retry package download for transient network/checksum failures.
            console.error(`Install attempt ${attempt} failed: ${error}`);
        }
    }
}

function installPydantic() {
    if (!runtimeInstalled()) {
        throw new Error(`Runtime package was not installed: ${LANGUAGE}@${VERSION}`);
    }

    try {
        execFileSync(PYTHON_BIN, ['-c', 'import pydantic'], { stdio: 'ignore' });
        return;
    } catch (_error) {
        // Pydantic is not available in runtime, install it below.
    }

    execFileSync(PYTHON_BIN, ['-m', 'ensurepip', '--upgrade'], { stdio: 'inherit' });
    execFileSync(PYTHON_BIN, ['-m', 'pip', 'install', '--no-cache-dir', '--upgrade', 'pip'], {
        stdio: 'inherit',
    });
    execFileSync(PYTHON_BIN, ['-m', 'pip', 'install', '--no-cache-dir', PYDANTIC_SPEC], {
        stdio: 'inherit',
    });
}

(async () => {
    await installRuntime();
    installPydantic();
})();
