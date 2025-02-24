import React, { useState } from 'react';
import Sidebar from './Sidebar';
import ProgressTable from './ProgressTable';
import { CSVLink } from 'react-csv';
import 'uikit/dist/css/uikit.min.css';

const MainPage = () => {
    const [rows, setRows] = useState([]);
    const [formData, setFormData] = useState({
        lastName: "山田",
        firstName: "太郎",
        lastNameKana: "ヤマダ",
        firstNameKana: "タロウ",
        zipCode: "123-4567",
        address: "東京都新宿区",
        phone: "03-1234-5678",
        email: "example@example.com",
        companyUrl: "https://example.com",
        message: "おとい"
    });
    
    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData((prevData) => ({
            ...prevData,
            [name]: value
        }));
    };
    

    const handleFileUpload = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            const text = event.target.result;
            const urls = text.split('\n').map(line => line.trim()).filter(line => line !== '');

            const newRows = urls.map(url => ({
                url,
                status: '待機',
                contactPage: '-',
                screenshot: '-',
                result: '-',
            }));
            setRows(newRows);
        };
        reader.readAsText(file);
    };

    const startProcessing = async () => {
        console.log("📌 送信する formData:", formData); // 🔍 ここでデバッグ用ログを追加
        for (let i = 0; i < rows.length; i++) {
            setRows(prevRows => prevRows.map((row, index) =>
                index === i ? { ...row, status: "処理中" } : row
            ));
    
            try {
                const response = await fetch('http://127.0.0.1:5000/submit-form', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Accept': 'application/json' },
                    mode: 'cors',
                    body: JSON.stringify({
                        urls: [rows[i].url],
                        form_data: formData,
                    }),
                });

                const data = await response.json();
                console.log("レスポンス:", data);

                const contactPage = data[0].contact_page || "-";
                const errorMessage = data[0].message || "その他エラーメッセージ";

                let resultMessage;
                if (data[0].status === "success") {
                    resultMessage = "送付成功";
                } else if (errorMessage.includes("スクレイピングNG")) {
                    resultMessage = "送付失敗（スプレイピング不可）";
                } else if (errorMessage.includes("問い合わせページが見つかりませんでした")) {
                    resultMessage = "送付失敗（問い合わせページが見つかりませんでした）";
                } else if (errorMessage.includes("営業利用禁止")) {
                    resultMessage = "送付失敗（送付不可：営業利用禁止）";
                } else if (errorMessage.includes("フォーム入力に失敗しました")) {
                    resultMessage = "送付失敗（フォーム入力に失敗しました）";
                } else {
                    resultMessage = `送付失敗（その他エラーメッセージ: ${errorMessage}）`;
                }

                setRows(prevRows => prevRows.map((row, index) =>
                    index === i ? {
                        ...row,
                        status: "処理済み",
                        contactPage: contactPage,
                        screenshot: data[0].screenshot ? data[0].screenshot : "-",
                        result: resultMessage,
                    } : row
                ));
    
            } catch (error) {
                console.error("エラー:", error);

                setRows(prevRows => prevRows.map((row, index) =>
                    index === i ? {
                        ...row,
                        status: "処理済み",
                        contactPage: "-",
                        screenshot: "-",
                        result: `送付失敗（その他エラーメッセージ: ${error.message}）`,
                    } : row
                ));
            }
        }
    };

    // CSV ダウンロード用ヘッダーとデータ
    const csvHeaders = [
        { label: 'URL', key: 'url' },
        { label: 'ステータス', key: 'status' },
        { label: '問い合わせURL', key: 'contactPage' },
        { label: 'スクリーンショットURL', key: 'screenshot' },
        { label: '送信結果', key: 'result' },
    ];

    return (
        <div className="uk-grid uk-grid-collapse uk-height-viewport">
            <Sidebar formData={formData} onInputChange={handleInputChange} />
            <div className="uk-width-expand uk-padding">
                <div className="button-bar uk-margin-bottom">
                    <input
                        className=""
                        type="file"
                        accept=".csv"
                        onChange={handleFileUpload}
                    />
                    <button className="uk-button uk-button-primary uk-margin-right" onClick={startProcessing}>
                        スタート
                    </button>
                    <CSVLink className="uk-button uk-button-secondary" data={rows} headers={csvHeaders} filename="progress_data.csv">
                        CSV ダウンロード
                    </CSVLink>
                </div>
                <ProgressTable rows={rows} />
            </div>
        </div>
    );
};

export default MainPage;
