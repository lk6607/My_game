<?py import helper ?>

local creat_role = {
<?py for data in creat_role: ?>
    [${data['id']}] = {
        id = ${data['id']},
        reward = ${helper.lua_split_items(str(data['reward']))},
        coin_reward = {${data['coin_reward']}},
        reward1_extra_desc = ${as_escaped(helper.client_language(data['reward1_extra_desc']))},
        reward2_extra_desc = ${as_escaped(helper.client_language(data['reward2_extra_desc']))},
    },
<?py #endfor ?>
}

local creat_speak = {
<?py for data in creat_speak: ?>
    [${data['id']}] = {
        id = ${data['id']},
        type = ${data['type']},
        steep = ${data['steep'] if data['steep'] != '' else 0} ,
        player = ${data['player'] if data['player'] != '' else 0} ,
        painting = "${data['painting']}",
        picture = "${data['picture']}",
        role_type = ${as_escaped(helper.client_language(data['role_type']))},
        desc = ${as_escaped(helper.client_language(data['desc']))},
    },
<?py #endfor ?>
}

local story_int = {
<?py for data in story_int: ?>
    [${data['id']}] = {
        id = ${data['id']},
        season = ${data['season']},
        pic = '${data['pic']}',
        desc = ${as_escaped(helper.client_language(data['desc']))},
    },
<?py #endfor ?>
}

local creat_regional = {
<?py for data in creat_regional: ?>
    [${data['id']}] = {
        id = ${data['id']},
        minIcon = '${data['minIcon']}',
        selectPos = {${data['selectPos']}},
        name = ${as_escaped(helper.client_language(data['name']))},
        characteristic = ${as_escaped(helper.client_language(data['characteristic']))},
        attr = ${helper.lua_split_items(str(data['attr']))},
        desc = ${as_escaped(helper.client_language(data['desc']))},
    },
<?py #endfor ?>
}

local creat_role_icon = {
<?py for data in creat_role_icon: ?>
    [${data['id']}] = {
        id = ${data['id']},
        gender = ${data['gender']},
        painting = "${data['painting']}",
        head_1 = "${data['head_1']}",
        head_2 = "${data['head_2']}",
        head_3 = "${data['head_3']}",
		picture = "${data['picture']}",
    },
<?py #endfor ?>
}

return {
    creat_role = creat_role,
    story_int = story_int,
    creat_speak = creat_speak,
    creat_regional = creat_regional,   
    creat_role_icon = creat_role_icon,   
}