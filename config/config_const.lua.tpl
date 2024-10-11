<?py max_len = max([len(d['name']) for d in all_data]) ?>
return {
<?py for data in all_data: ?>
<?py    space = " " * (max_len - len(data['name'])) ?>
	${data['name'] + space} = ${data['val']},
<?py #endfor ?>
}