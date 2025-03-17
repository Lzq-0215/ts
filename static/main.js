/*
@author: 梁卓权 3122004397
@create: 2025-01-05
@last_update: 2025-01-05
@description: html中所使用的js通用函数
@version: 1.0
*/

// 显示提示信息
function showAlert(message, isSuccess) {
    const alert = document.createElement('div');
    alert.className = `alert ${isSuccess ? 'alert-success' : 'alert-error'}`;
    alert.style.display = 'block';
    alert.textContent = message;
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 3000);
}

// 模态框通用函数
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    document.body.style.overflow = 'auto';
}

// 点击模态框外部关闭模态框
window.onclick = function(event) {
    const modals = document.getElementsByClassName('modal');
    for (let modal of modals) {
        if (event.target == modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    }
}

// 通用的API请求函数
async function apiRequest(url, method, data) {
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message || '操作成功', true);
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            showAlert(result.message || '操作失败', false);
        }
        
        return result;
    } catch (error) {
        showAlert('操作失败: ' + error, false);
        throw error;
    }
} 