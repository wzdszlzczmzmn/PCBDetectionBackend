from rest_framework import status

from . import models
from . import calculation
from rest_framework.decorators import api_view
from rest_framework.response import Response


def update():
    models.DataTable.update()


# Create your views here.
@api_view(['GET'])
def getProductStatus(request):
    # 返回残次品和良品数量
    start_date = request.query_params.get('startTime')
    end_date = request.query_params.get('endTime')
    line_no = request.query_params.get('productLineId')
    if line_no == '\"\"':
        line_no = None
    categories = calculation.get_categories(start_date, end_date, line_no)
    res = calculation.get_amount_list(start_date, end_date, line_no)
    res = {
        "categories": categories,
        "series": [{
            "name": "良品",
            "data": res["total_perfect_pcb_amount"],
        },
            {
                "name": "残次品",
                "data": res["total_defective_pcb_amount"],
            }]
    }
    return Response(res, status=status.HTTP_200_OK)


@api_view(['GET'])
def getProductLineList(request):
    res = list(calculation.getProductLineList())
    res = {
        "productLineList": res
    }
    return Response(res, status=status.HTTP_200_OK)


@api_view(['GET'])
def getDefectStatus(request):
    dic = calculation.defect_type("translation")
    start_date = request.query_params.get('startTime')
    end_date = request.query_params.get('endTime')
    line_no = request.query_params.get('productLineId')
    defect_type = request.query_params.get('defectType')
    if line_no == '\"\"':
        line_no = None
    if defect_type == '\"\"':
        defect_type = None
    is_ratio = request.query_params.get('percentage')
    categories = calculation.get_categories(start_date, end_date, line_no)
    if defect_type is not None:
        defect_type = dic[defect_type]
    if is_ratio == 'true':
        if defect_type is not None:     # 查询所有缺陷的占比
            res = {
                "categories": categories,
                "series": [{
                    "name": dic[defect_type],
                    "data": calculation.cal_ratio_list(start_date, end_date, defect_type, line_no),
                }],
            }
        else:   # 查询某类型的缺陷的占比
            series = []
            for i in calculation.defect_type():    # 缺陷种类列表
                series.append({
                    "name": dic[i],
                    "data": calculation.cal_ratio_list(start_date, end_date, i, line_no)
                })
            res = {
                "categories": categories,
                "series": series
            }

    else:
        if defect_type is not None:  # 查询某类型的缺陷的数量
            res = calculation.cal_amount_typeSpec(start_date, end_date, defect_type, line_no)
            res = {
                "categories": categories,
                "series": {
                    "name": dic[defect_type],
                    "data": res["result"],
                }
            }
        else:   # 查询所有类型的缺陷的数量
            series = []
            for i in calculation.defect_type():    # 缺陷类型列表
                series.append({
                    "name": i,
                    "data": calculation.cal_amount_typeSpec(start_date, end_date, i, line_no)["result"]
                })
            res = {
                "categories": categories,
                "series": series
            }

    return Response(res, status=status.HTTP_200_OK)


@api_view(['GET'])
def getYieldStatus(request):
    start_date = request.query_params.get('startTime')
    end_date = request.query_params.get('endTime')
    line_no = request.query_params.get('productLineId')
    if line_no == '\"\"':
        line_no = None
    categories = calculation.get_categories(start_date, end_date, line_no)

    if line_no is None:
        series = []
        for i in list(calculation.getProductLineList()):
            series.append({
                "name": calculation.convert_line_no(i),
                "data": calculation.cal_pass_rate(start_date, end_date, line_no=i)
            })
        res = {
            "categories": categories,
            "series": series
        }
        return Response(res, status=status.HTTP_200_OK)
    else:
        res = calculation.cal_pass_rate(start_date, end_date, line_no)
        res = {
            "categories": categories,
            "series": [
                {
                    "name": calculation.convert_line_no(line_no),
                    "data": res,
                }
            ]
        }
        return Response(res, status=status.HTTP_200_OK)
