
function getListRole(){
    var data = {};
    var output = [];
    $.ajax({
        url: GET_LIST_ROLE,
        type: "POST",
        async: false,
        data: encodeURIComponent(JSON.stringify(data)),
        success: function(resp){
            var result = resp.result;
            output = result;
        }
    });
    return output;
}
function getListUser(){
    var data = {};
    var output = [];
    $.ajax({
        url: GET_LIST_USER,
        type: "POST",
        async: false,
        data: encodeURIComponent(JSON.stringify(data)),
        success: function(resp){
            var result = resp.result;
            output = result;
        }
    });
    return output;
}
function getUserRole(){
    var data = {};
    var output = [];
    $.ajax({
        url: GET_USER_ROLE,
        type: "POST",
        async: false,
        data: encodeURIComponent(JSON.stringify(data)),
        success: function(resp){
            var result = resp.result;
            output = result;
        }
    });
    return output;
}
function createRoleCardContent (){
    var role = getListRole();
    var roleElm = document.getElementById('role_block');
    for (var i = 0; i < role.length; i++) {
        let roleId = role[i]['role_id'];
        let roleName = role[i]['role_name'];
        let itemElm = document.createElement("DIV");
        itemElm.className = 'ctcard__content-item';
        let content = '';
        content += `<input type="text" value='${roleName}'>
        <a class='item__remove remove_role' ><i class="fas fa-minus-circle"></i></a>`;
        itemElm.innerHTML = content;
        roleElm.appendChild(itemElm);
    }
}

function createUserRoleCardContent(){
    let userRole = getUserRole();
    let userRoleElm = document.getElementById('user_role_block');
    let user = getListUser();
    let role = getListRole();
    for (var i = 0; i < userRole.length; i++) {
        let roleId = userRole[i]['role_id'];
        let roleName = userRole[i]['role_name'];
        let userName = userRole[i]['user_name'];
        let userId = userRole[i]['user_id'];
        let itemElm = document.createElement("DIV");
        itemElm.className = 'ctcard__content-item';
        let content = '';
        // role
        content += `<select name="" id="" class="item__user">`;
        content += `<option value=""></option>`;
        for (var j = 0; j < user.length; j++) {
            let userName2 = user[j]['user_name'];
            let userId2 = user[j]['user_id'];
            let select = '';
            if (userName == userName2) {
                select = 'selected';
            }
            content += `<option value="${userId2}" ${select}>${userName2}</option>`;
        }
        content += `</select>`;
        
        // user
        content += `<select name="" id="" class="item__role">`;
        content += `<option value=""></option>`;
        for (var j2 = 0; j2 < role.length; j2++) {
            let roleName2 = role[j2]['role_name'];
            let roleId2 = role[j2]['role_id'];
            let select = '';
            if (roleName == roleName2) {
                select = 'selected';
            }
            content += `<option value="${roleId2}" ${select}>${roleName2}</option>`;
        }
        content += `</select>`;
        content += `<a class='item__remove remove_user_role'><i class="fas fa-minus-circle"></i></a>`;
        itemElm.innerHTML = content;
        userRoleElm.appendChild(itemElm);
    }
}
function getDataToUpdate(){
    var data = {};
    data['role'] = [];
    data['user_role'] = [];
    // get list role
    let roleElm = document.getElementById('role_block');
    let listInput = roleElm.querySelectorAll('input');
    for (var i = 0; i < listInput.length; i++) {
        let role  = listInput[i].value;
        if (role.trim()) {
            data['role'].push(role.trim()); 
        }
    }
    // get user role
    let userRoleElm = document.getElementById('user_role_block');
    let listItem = userRoleElm.querySelectorAll('.ctcard__content-item');
    for (var i2 = 0; i2 < listItem.length; i2++) {
        let itemElm  = listItem[i2];
        let userSelectElm = itemElm.querySelector('.item__user')
        let user = userSelectElm.value;
        let roleSelectElm = itemElm.querySelector('.item__role')
        let role = roleSelectElm.value;
        if (!role.trim() && !user.trim()) {
            continue;
        }
        if (!role.trim()) {
            alert('Role name is empty!');
            return null;
        }
        if (!user.trim()) {
            alert('User name is empty!');
            return null;
        } 
        data['user_role'].push([user, role]); 
        
    }
    return data;
}
$(document).ready(function(){
    createRoleCardContent();
    createUserRoleCardContent();
    $('#new_user_role').click(function(){
        let userRoleElm = document.getElementById('user_role_block');
        let user = getListUser();
        let role = getListRole();
        let itemElm = document.createElement("DIV");
        itemElm.className = 'ctcard__content-item';
        let content = '';
        // role
        content += `<select name="" id="" class="item__user">`;
        content += `<option value=""></option>`;
        for (var j = 0; j < user.length; j++) {
            let userName2 = user[j]['user_name'];
            let userId2 = user[j]['user_id'];
            content += `<option value="${userId2}">${userName2}</option>`;
        }
        content += `</select>`;
        // user
        content += `<select name="" id="" class="item__role">`;
        content += `<option value=""></option>`;
        for (var j2 = 0; j2 < role.length; j2++) {
            let roleName2 = role[j2]['role_name'];
            let roleId2 = role[j2]['role_id'];
            let select = '';
            content += `<option value="${roleId2}">${roleName2}</option>`;
        }
        content += `</select>`;
        content += `<a class='item__remove remove_user_role'><i class="fas fa-minus-circle"></i></a>`;
        itemElm.innerHTML = content;
        userRoleElm.appendChild(itemElm);
    })
    $('#new_role').click(function(){
        var roleElm = document.getElementById('role_block');
        let itemElm = document.createElement("DIV");
        itemElm.className = 'ctcard__content-item';
        let content = '';
        content += `<input type="text" value=''>
        <a class='item__remove remove_role'><i class="fas fa-minus-circle"></i></a>`;
        itemElm.innerHTML = content;
        roleElm.appendChild(itemElm);
    })
    $(document).on('click', '.remove_user_role', function(){
        var parentElm = $(this).parent();
        parentElm.remove();
    })
    $(document).on('click', '.remove_role', function(){
        var parentElm = $(this).parent();
        parentElm.remove();
    })
    $(document).on('change', 'input, select', function(){
        $('#save').prop('disabled', false);
    })
    $(document).on('click', '.remove_user_role, .remove_role', function(){
        $('#save').prop('disabled', false);
    })
    $('#save').click(function(){
        var data = getDataToUpdate();
        if (data != null) {
            $('#overlay_loader').show();
            $.ajax({
                url: UPDATE_ADMIN_USER_ROLE,
                type: "POST",
                data: encodeURIComponent(JSON.stringify(data)),
                success: function(resp){
                    location.reload();
                }
            });
        } 
    })
})

