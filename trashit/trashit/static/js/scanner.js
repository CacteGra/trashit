// --- Scan Wrapper (Quagga) ---

function scanWrapper() {
    const modal = document.getElementById('wrapperModal');
    if (!modal) return;
    $(modal).modal('toggle');

    Quagga.init({
        inputStream: {
            name: 'Live',
            type: 'LiveStream',
            target: document.querySelector('#scan-viewport')
        },
        decoder: { readers: ['ean_reader'] }
    }, function (err) {
        if (err) return console.error(err);
        console.log('Quagga initialized');
        Quagga.start();
    });

    let codes = [];

    Quagga.onDetected(function (result) {
        const code = result.codeResult.code;
        codes.push(code);

        const getRecurringValues = (arr) => {
            const counts = arr.reduce((acc, curr) => {
                acc[curr] = (acc[curr] || 0) + 1;
                return acc;
            }, {});
            return Object.entries(counts)
                .filter(([___, count]) => count > 1)
                .sort((a, b) => b[1] - a[1]);
        };

        const recurring = getRecurringValues(codes);

        // Only proceed if the most recurring item appears >= 5 times AND we aren't currently scanning
        const itemNumber = recurring.length === 0 ? 1 : recurring[0][1];

        if (itemNumber >= 5 && !window.scanning) {
            window.scanning = true;
            $.get(scanUrl, { code: recurring[0][0] })
                .done(function (response) {
                    $scanResult.innerHTML = response.map(r => r.html).join('');
                    window.scanning = false;
                })
                .fail(() => {
                    // Handle API failure gracefully
                    window.scanning = false;
                });
        }
    });
}