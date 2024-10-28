const passwordConfirmFld = document.getElementById('passwordConfirmFld');
const passwordFld = document.getElementById('passwordFld');

passwordConfirmFld.addEventListener('input', function(){
    let password = passwordFld.value;
    let passwordConfirm = passwordConfirmFld.value;

    if(password.length <= passwordConfirm.length && password.length > 0){
        if(password === passwordConfirm){
            passwordFld.style.borderColor = '#2ecc71';
            passwordConfirmFld.style.borderColor = '#2ecc71';
        }
        else{
            passwordFld.style.borderColor = '#e74c3c';
            passwordConfirmFld.style.borderColor = '#e74c3c';
        }
    }
    else{
        passwordFld.style.borderColor = '#ccc';
        passwordConfirmFld.style.borderColor = '#ccc';
    }
});

function checkPassword(attribute){
    const catImage = document.getElementById('catImage');
    if (passwordFld.type === 'password') {
        passwordFld.type = 'text';
        attribute.src = attribute.getAttribute('data-hide-src');
        catImage.style.opacity = '1';
        catImage.style.transform = `translateX(43px)`;
        catImage.style.zIndex = '1';
    } else {
        passwordFld.type = 'password';
        attribute.src = attribute.getAttribute('data-show-src');
        catImage.style.opacity = '0';
        catImage.style.transform = `translateX(0px)`;
        catImage.style.zIndex = '-1';
    }
}

function checkPassword2(attribute){
    const catImage = document.getElementById('catImage2');
    if (passwordConfirmFld.type === 'password') {
        passwordConfirmFld.type = 'text';
        attribute.src = attribute.getAttribute('data-hide-src');
        catImage.style.opacity = '1';
        catImage.style.transform = `translateX(50px)`;
        catImage.style.zIndex = '1';
    } else {
        passwordConfirmFld.type = 'password';
        attribute.src = attribute.getAttribute('data-show-src');
        catImage.style.opacity = '0';
        catImage.style.transform = `translateX(0px)`;
        catImage.style.zIndex = '-1';
    }
}