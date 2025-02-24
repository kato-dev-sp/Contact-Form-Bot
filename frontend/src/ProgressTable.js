import React from 'react';

const ProgressTable = ({ rows }) => {
    return (
        <table className="uk-table uk-table-divider">
            <thead>
                <tr>
                    <th>URL</th>
                    <th>ステータス</th>
                    <th>問い合わせURL</th>
                    <th>スクリーンショットURL</th>
                    <th>送信結果</th>
                </tr>
            </thead>
            <tbody>
                {rows.map((row, index) => (
                    <tr key={index}>
                        <td>{row.url}</td>
                        <td>{row.status}</td>
                        <td>
                            {row.contactPage !== "-" ? (
                                <a href={row.contactPage} target="_blank" rel="noopener noreferrer">リンク</a>
                            ) : "-"}
                        </td>
                        <td>
                            {row.screenshot !== "-" ? (
                                <a href={row.screenshot} target="_blank" rel="noopener noreferrer">リンク</a>
                            ) : "-"}
                        </td>
                        <td>{row.result}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

export default ProgressTable;
