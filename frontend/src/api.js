// frontend/src/api.js

export async function detectContactPage(url) {
    try {
        const response = await fetch('http://127.0.0.1:5000/detect-contact-page', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }),
        });

        if (!response.ok) {
            throw new Error(`HTTPエラー: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('APIリクエストエラー:', error);
        return { status: 'error', message: error.message };
    }
}

export async function submitForm(contactPage, formData) {
    try {
        const response = await fetch('http://127.0.0.1:5000/submit-form', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ contact_page: contactPage, form_data: formData }),
        });

        if (!response.ok) {
            throw new Error(`HTTPエラー: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('APIリクエストエラー:', error);
        return { status: 'error', message: error.message };
    }
}
