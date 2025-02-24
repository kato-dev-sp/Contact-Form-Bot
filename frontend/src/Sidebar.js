import React, { useState } from 'react';

const Sidebar = ({ formData, onInputChange }) => {
    const [defaultValues] = useState({
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

    // `null` または `undefined` の場合のみデフォルト値を適用
    const getValue = (key) => (formData[key] !== null && formData[key] !== undefined ? formData[key] : defaultValues[key]);

    return (
        <aside className="uk-width-1-4 uk-background-muted uk-padding">
            <h3>入力フォーム</h3>
            <form>
                <div className="uk-margin">
                    <label className="uk-form-label">姓</label>
                    <input
                        className="uk-input"
                        type="text"
                        name="lastName"
                        value={getValue("lastName")}
                        onChange={onInputChange}
                    />
                </div>
                <div className="uk-margin">
                    <label className="uk-form-label">名</label>
                    <input
                        className="uk-input"
                        type="text"
                        name="firstName"
                        value={getValue("firstName")}
                        onChange={onInputChange}
                    />
                </div>
                <div className="uk-margin">
                    <label className="uk-form-label">姓カナ</label>
                    <input
                        className="uk-input"
                        type="text"
                        name="lastNameKana"
                        value={getValue("lastNameKana")}
                        onChange={onInputChange}
                    />
                </div>
                <div className="uk-margin">
                    <label className="uk-form-label">名カナ</label>
                    <input
                        className="uk-input"
                        type="text"
                        name="firstNameKana"
                        value={getValue("firstNameKana")}
                        onChange={onInputChange}
                    />
                </div>
                <div className="uk-margin">
                    <label className="uk-form-label">郵便番号</label>
                    <input
                        className="uk-input"
                        type="text"
                        name="zipCode"
                        value={getValue("zipCode")}
                        onChange={onInputChange}
                    />
                </div>
                <div className="uk-margin">
                    <label className="uk-form-label">住所</label>
                    <input
                        className="uk-input"
                        type="text"
                        name="address"
                        value={getValue("address")}
                        onChange={onInputChange}
                    />
                </div>
                <div className="uk-margin">
                    <label className="uk-form-label">電話番号</label>
                    <input
                        className="uk-input"
                        type="text"
                        name="phone"
                        value={getValue("phone")}
                        onChange={onInputChange}
                    />
                </div>
                <div className="uk-margin">
                    <label className="uk-form-label">メールアドレス</label>
                    <input
                        className="uk-input"
                        type="email"
                        name="email"
                        value={getValue("email")}
                        onChange={onInputChange}
                    />
                </div>
                <div className="uk-margin">
                    <label className="uk-form-label">自社HP URL</label>
                    <input
                        className="uk-input"
                        type="text"
                        name="companyUrl"
                        value={getValue("companyUrl")}
                        onChange={onInputChange}
                    />
                </div>
                <div className="uk-margin">
                    <label className="uk-form-label">お問い合わせ内容</label>
                    <textarea
                        className="uk-textarea"
                        name="message"
                        value={getValue("message")}
                        onChange={onInputChange}
                        rows="4"
                    />
                </div>
            </form>
        </aside>
    );
};

export default Sidebar;
