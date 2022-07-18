def tag_operator(objs, some_model, some_data_storage, model_attr):
    for obj in objs:
        some_model.objects.create(recipe=model_attr, tag=obj)
        some_data_storage.append(obj)


def ingredient_operator(
    objs, some_model, model_attr, some_data_storage, another_data_storage1, err
):
    for ingredient in objs:
        ing = ingredient.get('id')
        amount = ingredient.get('amount')
        new_recing = some_model(
            recipe=model_attr,
            ingredient=ing,
            amount=amount
        )
        another_data_storage1.append(new_recing)
        some_data_storage.append(ing)
