import random
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import httpx
from ..config import settings
from ..models.schemas import DeviceTelemetry, SevereLocation, CitySummary, RoadNode, FloodedRoad, FloodZone

ROADS_DATA: List[Dict[str, Any]] = [
    {
        "id": "road-01",
        "name": "Đường Phan Huy Ích",
        "district": "Gò Vấp - Tân Bình",
        "length_km": 3.4,
        "type": "ROAD",
        "base_water": 52.0,
        "max_water_cm": 52.0,
        "avg_water_cm": 35.4,
        "severity": "CRITICAL",
        "avoid_advice": "Ngập sâu đoạn Cầu Hy Vọng. Khuyên chuyển hướng sang đường Trường Chinh hoặc Quang Trung.",
        "coordinates": [
            [
                10.82346,
                106.62943
            ],
            [
                10.82349,
                106.62977
            ],
            [
                10.82313,
                106.62975
            ],
            [
                10.82312,
                106.62942
            ],
            [
                10.82338,
                106.62968
            ],
            [
                10.82365,
                106.6299
            ],
            [
                10.82432,
                106.63022
            ],
            [
                10.8246,
                106.63035
            ],
            [
                10.8249,
                106.63048
            ],
            [
                10.82548,
                106.63076
            ],
            [
                10.82585,
                106.63093
            ],
            [
                10.82635,
                106.63116
            ],
            [
                10.82679,
                106.63136
            ],
            [
                10.82712,
                106.6315
            ],
            [
                10.82742,
                106.63164
            ],
            [
                10.82792,
                106.63187
            ],
            [
                10.82835,
                106.63207
            ],
            [
                10.82874,
                106.63225
            ],
            [
                10.82932,
                106.63253
            ],
            [
                10.82963,
                106.63267
            ],
            [
                10.83035,
                106.63302
            ],
            [
                10.83076,
                106.63323
            ],
            [
                10.83105,
                106.63336
            ],
            [
                10.83142,
                106.63353
            ],
            [
                10.83193,
                106.63376
            ],
            [
                10.83229,
                106.63393
            ],
            [
                10.83283,
                106.63422
            ],
            [
                10.83381,
                106.63467
            ],
            [
                10.83443,
                106.63495
            ],
            [
                10.83472,
                106.63509
            ],
            [
                10.83525,
                106.63533
            ],
            [
                10.8359,
                106.63564
            ],
            [
                10.83623,
                106.6358
            ],
            [
                10.83652,
                106.63593
            ],
            [
                10.83683,
                106.63606
            ],
            [
                10.83735,
                106.63629
            ],
            [
                10.83772,
                106.63646
            ],
            [
                10.83818,
                106.63669
            ],
            [
                10.83853,
                106.63684
            ],
            [
                10.83905,
                106.63708
            ],
            [
                10.83961,
                106.63735
            ],
            [
                10.83998,
                106.63754
            ],
            [
                10.84031,
                106.6377
            ],
            [
                10.84082,
                106.63795
            ],
            [
                10.84145,
                106.63832
            ],
            [
                10.84177,
                106.63852
            ],
            [
                10.8421,
                106.63874
            ],
            [
                10.84245,
                106.63897
            ],
            [
                10.84292,
                106.63929
            ],
            [
                10.84338,
                106.63957
            ],
            [
                10.84383,
                106.63985
            ],
            [
                10.84415,
                106.64003
            ],
            [
                10.84429,
                106.64011
            ]
        ],
        "nodes": [
            {
                "id": "node-01",
                "name": "Ngã ba Trường Chinh",
                "lat": 10.82346,
                "lon": 106.62943,
                "latitude": 10.82346,
                "longitude": 106.62943,
                "base_water": 20.8,
                "water_level_cm": 20.8,
                "status": "ALERT"
            },
            {
                "id": "node-02",
                "name": "Đoạn giao Tây Thạnh",
                "lat": 10.82712,
                "lon": 106.6315,
                "latitude": 10.82712,
                "longitude": 106.6315,
                "base_water": 39.0,
                "water_level_cm": 39.0,
                "status": "WARNING"
            },
            {
                "id": "node-03",
                "name": "Rốn ngập Cầu Hy Vọng",
                "lat": 10.83283,
                "lon": 106.63422,
                "latitude": 10.83283,
                "longitude": 106.63422,
                "base_water": 52.0,
                "water_level_cm": 52.0,
                "status": "CRITICAL"
            },
            {
                "id": "node-04",
                "name": "Đoạn giao Huỳnh Văn Nghệ",
                "lat": 10.83905,
                "lon": 106.63708,
                "latitude": 10.83905,
                "longitude": 106.63708,
                "base_water": 41.6,
                "water_level_cm": 41.6,
                "status": "WARNING"
            },
            {
                "id": "node-05",
                "name": "Ngã ba Quang Trung",
                "lat": 10.84429,
                "lon": 106.64011,
                "latitude": 10.84429,
                "longitude": 106.64011,
                "base_water": 23.4,
                "water_level_cm": 23.4,
                "status": "ALERT"
            }
        ]
    },
    {
        "id": "road-02",
        "name": "Đường Nguyễn Văn Quá",
        "district": "Quận 12",
        "length_km": 4.1,
        "type": "ROAD",
        "base_water": 50.0,
        "max_water_cm": 50.0,
        "avg_water_cm": 34.0,
        "severity": "CRITICAL",
        "avoid_advice": "Ngập sâu đoạn Chợ Cầu. Khuyên phương tiện chuyển hướng sang QL1A hoặc đường Song Hành QL22.",
        "coordinates": [
            [
                10.82783,
                106.62674
            ],
            [
                10.82828,
                106.62678
            ],
            [
                10.82863,
                106.62682
            ],
            [
                10.82916,
                106.62688
            ],
            [
                10.82972,
                106.62705
            ],
            [
                10.83005,
                106.62715
            ],
            [
                10.83051,
                106.62731
            ],
            [
                10.83117,
                106.62753
            ],
            [
                10.83184,
                106.62773
            ],
            [
                10.83265,
                106.62799
            ],
            [
                10.83296,
                106.6281
            ],
            [
                10.83341,
                106.62824
            ],
            [
                10.83418,
                106.62846
            ],
            [
                10.83509,
                106.62873
            ],
            [
                10.83544,
                106.62882
            ],
            [
                10.83573,
                106.6289
            ],
            [
                10.83635,
                106.62907
            ],
            [
                10.83672,
                106.62917
            ],
            [
                10.83719,
                106.6293
            ],
            [
                10.83779,
                106.62946
            ],
            [
                10.83825,
                106.62958
            ],
            [
                10.83874,
                106.6297
            ],
            [
                10.83964,
                106.62994
            ],
            [
                10.84046,
                106.6301
            ],
            [
                10.84096,
                106.6302
            ],
            [
                10.84129,
                106.63031
            ],
            [
                10.84173,
                106.63048
            ],
            [
                10.84206,
                106.63061
            ],
            [
                10.84238,
                106.63075
            ],
            [
                10.84278,
                106.63091
            ],
            [
                10.84341,
                106.63118
            ],
            [
                10.84374,
                106.63132
            ],
            [
                10.84431,
                106.63181
            ],
            [
                10.84473,
                106.63222
            ],
            [
                10.84539,
                106.6328
            ],
            [
                10.84562,
                106.633
            ],
            [
                10.84585,
                106.6332
            ],
            [
                10.84612,
                106.63347
            ],
            [
                10.84647,
                106.63391
            ],
            [
                10.8468,
                106.63432
            ],
            [
                10.84737,
                106.63502
            ],
            [
                10.84815,
                106.63556
            ],
            [
                10.84887,
                106.63601
            ],
            [
                10.84947,
                106.63636
            ],
            [
                10.84979,
                106.63654
            ],
            [
                10.85049,
                106.63694
            ],
            [
                10.85098,
                106.63721
            ],
            [
                10.85158,
                106.63754
            ],
            [
                10.85231,
                106.63785
            ],
            [
                10.85291,
                106.63805
            ],
            [
                10.85328,
                106.63817
            ],
            [
                10.85403,
                106.63842
            ],
            [
                10.85433,
                106.63853
            ],
            [
                10.85467,
                106.63868
            ],
            [
                10.85506,
                106.63886
            ],
            [
                10.85546,
                106.63903
            ],
            [
                10.85584,
                106.6392
            ],
            [
                10.85632,
                106.63941
            ],
            [
                10.85647,
                106.63941
            ]
        ],
        "nodes": [
            {
                "id": "node-06",
                "name": "Cầu Tham Lương - Trường Chinh",
                "lat": 10.82783,
                "lon": 106.62674,
                "latitude": 10.82783,
                "longitude": 106.62674,
                "base_water": 20.0,
                "water_level_cm": 20.0,
                "status": "ALERT"
            },
            {
                "id": "node-07",
                "name": "Giao lộ Đông Hưng Thuận",
                "lat": 10.83544,
                "lon": 106.62882,
                "latitude": 10.83544,
                "longitude": 106.62882,
                "base_water": 37.5,
                "water_level_cm": 37.5,
                "status": "WARNING"
            },
            {
                "id": "node-08",
                "name": "Rốn ngập Chợ Cầu",
                "lat": 10.84278,
                "lon": 106.63091,
                "latitude": 10.84278,
                "longitude": 106.63091,
                "base_water": 50.0,
                "water_level_cm": 50.0,
                "status": "CRITICAL"
            },
            {
                "id": "node-09",
                "name": "Đoạn giao Tô Ký",
                "lat": 10.84979,
                "lon": 106.63654,
                "latitude": 10.84979,
                "longitude": 106.63654,
                "base_water": 40.0,
                "water_level_cm": 40.0,
                "status": "WARNING"
            },
            {
                "id": "node-10",
                "name": "Ngã ba QL1A Tân Thới Hiệp",
                "lat": 10.85647,
                "lon": 106.63941,
                "latitude": 10.85647,
                "longitude": 106.63941,
                "base_water": 22.5,
                "water_level_cm": 22.5,
                "status": "ALERT"
            }
        ]
    },
    {
        "id": "road-03",
        "name": "Đường Huỳnh Tấn Phát",
        "district": "Quận 7",
        "length_km": 4.8,
        "type": "ROAD",
        "base_water": 56.0,
        "max_water_cm": 56.0,
        "avg_water_cm": 38.1,
        "severity": "CRITICAL",
        "avoid_advice": "Triều cường dâng ngập đoạn Trần Trọng Cung. Khuyên đi đường Nguyễn Thị Thập hoặc Nguyễn Lương Bằng.",
        "coordinates": [
            [
                10.73791,
                106.73034
            ],
            [
                10.73843,
                106.73026
            ],
            [
                10.73877,
                106.7302
            ],
            [
                10.73928,
                106.73013
            ],
            [
                10.73964,
                106.73007
            ],
            [
                10.73996,
                106.73002
            ],
            [
                10.7407,
                106.72991
            ],
            [
                10.74141,
                106.7298
            ],
            [
                10.74209,
                106.72969
            ],
            [
                10.74268,
                106.7296
            ],
            [
                10.74328,
                106.72951
            ],
            [
                10.74373,
                106.72944
            ],
            [
                10.7448,
                106.72928
            ],
            [
                10.74514,
                106.72923
            ],
            [
                10.74338,
                106.72959
            ],
            [
                10.74375,
                106.72954
            ],
            [
                10.74483,
                106.72937
            ],
            [
                10.74515,
                106.72932
            ],
            [
                10.7462,
                106.72918
            ],
            [
                10.74669,
                106.72911
            ],
            [
                10.7471,
                106.72905
            ],
            [
                10.74753,
                106.72898
            ],
            [
                10.74832,
                106.72887
            ],
            [
                10.74876,
                106.72884
            ],
            [
                10.74963,
                106.72877
            ],
            [
                10.74998,
                106.72875
            ],
            [
                10.75092,
                106.72867
            ],
            [
                10.75144,
                106.72863
            ],
            [
                10.75227,
                106.72858
            ],
            [
                10.75265,
                106.72855
            ]
        ],
        "nodes": [
            {
                "id": "node-11",
                "name": "Chân cầu Tân Thuận",
                "lat": 10.73791,
                "lon": 106.73034,
                "latitude": 10.73791,
                "longitude": 106.73034,
                "base_water": 22.4,
                "water_level_cm": 22.4,
                "status": "ALERT"
            },
            {
                "id": "node-12",
                "name": "Ngã tư Nguyễn Thị Thập",
                "lat": 10.74141,
                "lon": 106.7298,
                "latitude": 10.74141,
                "longitude": 106.7298,
                "base_water": 42.0,
                "water_level_cm": 42.0,
                "status": "WARNING"
            },
            {
                "id": "node-13",
                "name": "Rốn ngập Trần Trọng Cung",
                "lat": 10.74375,
                "lon": 106.72954,
                "latitude": 10.74375,
                "longitude": 106.72954,
                "base_water": 56.0,
                "water_level_cm": 56.0,
                "status": "CRITICAL"
            },
            {
                "id": "node-14",
                "name": "Chân cầu Phú Mỹ",
                "lat": 10.74832,
                "lon": 106.72887,
                "latitude": 10.74832,
                "longitude": 106.72887,
                "base_water": 44.8,
                "water_level_cm": 44.8,
                "status": "WARNING"
            },
            {
                "id": "node-15",
                "name": "Chân cầu Phú Xuân",
                "lat": 10.75265,
                "lon": 106.72855,
                "latitude": 10.75265,
                "longitude": 106.72855,
                "base_water": 25.2,
                "water_level_cm": 25.2,
                "status": "ALERT"
            }
        ]
    },
    {
        "id": "road-04",
        "name": "Đường Trần Xuân Soạn",
        "district": "Quận 7",
        "length_km": 3.6,
        "type": "ROAD",
        "base_water": 53.0,
        "max_water_cm": 53.0,
        "avg_water_cm": 36.1,
        "severity": "CRITICAL",
        "avoid_advice": "Bờ kè Kênh Tẻ nước tràn bờ. Khuyên chuyển hướng sang đường Nguyễn Thị Thập hoặc đường số 15.",
        "coordinates": [
            [
                10.75101,
                106.69107
            ],
            [
                10.75108,
                106.69152
            ],
            [
                10.75115,
                106.69187
            ],
            [
                10.75133,
                106.69242
            ],
            [
                10.75142,
                106.69287
            ],
            [
                10.75149,
                106.69321
            ],
            [
                10.75159,
                106.69372
            ],
            [
                10.75164,
                106.69403
            ],
            [
                10.7517,
                106.69445
            ],
            [
                10.7517,
                106.69535
            ],
            [
                10.7517,
                106.69566
            ],
            [
                10.75171,
                106.6961
            ],
            [
                10.75173,
                106.69675
            ],
            [
                10.75172,
                106.69733
            ],
            [
                10.75172,
                106.69779
            ],
            [
                10.75172,
                106.69849
            ],
            [
                10.75172,
                106.69893
            ],
            [
                10.75173,
                106.69928
            ],
            [
                10.75173,
                106.69975
            ],
            [
                10.75173,
                106.70019
            ],
            [
                10.75176,
                106.7011
            ],
            [
                10.75176,
                106.70145
            ],
            [
                10.75176,
                106.70179
            ],
            [
                10.75177,
                106.70215
            ],
            [
                10.75177,
                106.70285
            ],
            [
                10.75178,
                106.70355
            ],
            [
                10.75178,
                106.70401
            ],
            [
                10.75179,
                106.70469
            ],
            [
                10.75179,
                106.70501
            ],
            [
                10.75179,
                106.70561
            ],
            [
                10.75179,
                106.70598
            ],
            [
                10.7518,
                106.70669
            ],
            [
                10.75181,
                106.70743
            ],
            [
                10.75182,
                106.70885
            ],
            [
                10.75182,
                106.70949
            ],
            [
                10.75183,
                106.71031
            ],
            [
                10.75183,
                106.7112
            ],
            [
                10.75184,
                106.71184
            ],
            [
                10.75184,
                106.7122
            ],
            [
                10.75185,
                106.71302
            ],
            [
                10.75185,
                106.71343
            ],
            [
                10.75186,
                106.71404
            ],
            [
                10.75186,
                106.71463
            ],
            [
                10.75186,
                106.71498
            ],
            [
                10.75187,
                106.71574
            ],
            [
                10.75186,
                106.7164
            ],
            [
                10.75187,
                106.71692
            ],
            [
                10.75189,
                106.71725
            ],
            [
                10.75197,
                106.71758
            ],
            [
                10.75212,
                106.71791
            ],
            [
                10.75228,
                106.71818
            ],
            [
                10.75256,
                106.71867
            ],
            [
                10.75279,
                106.71905
            ],
            [
                10.75298,
                106.71935
            ],
            [
                10.7532,
                106.71963
            ],
            [
                10.75413,
                106.72038
            ],
            [
                10.75499,
                106.72088
            ],
            [
                10.75539,
                106.72105
            ],
            [
                10.75588,
                106.72128
            ],
            [
                10.75638,
                106.72151
            ],
            [
                10.7569,
                106.72178
            ],
            [
                10.75729,
                106.72198
            ],
            [
                10.75749,
                106.72229
            ]
        ],
        "nodes": [
            {
                "id": "node-16",
                "name": "Chân cầu Tân Thuận 2",
                "lat": 10.75101,
                "lon": 106.69107,
                "latitude": 10.75101,
                "longitude": 106.69107,
                "base_water": 21.2,
                "water_level_cm": 21.2,
                "status": "ALERT"
            },
            {
                "id": "node-17",
                "name": "Bờ kè Lâm Văn Bền",
                "lat": 10.75172,
                "lon": 106.69849,
                "latitude": 10.75172,
                "longitude": 106.69849,
                "base_water": 39.8,
                "water_level_cm": 39.8,
                "status": "WARNING"
            },
            {
                "id": "node-18",
                "name": "Rốn ngập Cầu Kênh Tẻ",
                "lat": 10.7518,
                "lon": 106.70669,
                "latitude": 10.7518,
                "longitude": 106.70669,
                "base_water": 53.0,
                "water_level_cm": 53.0,
                "status": "CRITICAL"
            },
            {
                "id": "node-19",
                "name": "Chân cầu Rạch Ông",
                "lat": 10.75189,
                "lon": 106.71725,
                "latitude": 10.75189,
                "longitude": 106.71725,
                "base_water": 42.4,
                "water_level_cm": 42.4,
                "status": "WARNING"
            },
            {
                "id": "node-20",
                "name": "Chân cầu Chữ Y",
                "lat": 10.75749,
                "lon": 106.72229,
                "latitude": 10.75749,
                "longitude": 106.72229,
                "base_water": 23.9,
                "water_level_cm": 23.9,
                "status": "ALERT"
            }
        ]
    },
    {
        "id": "road-05",
        "name": "Đường Nguyễn Hữu Cảnh",
        "district": "Bình Thạnh",
        "length_km": 3.2,
        "type": "ROAD",
        "base_water": 46.0,
        "max_water_cm": 46.0,
        "avg_water_cm": 31.3,
        "severity": "WARNING",
        "avoid_advice": "Ngập đoạn hầm chui và The Manor. Khuyên đi vòng qua đường Điện Biên Phủ hoặc đường Ung Văn Khiêm.",
        "coordinates": [
            [
                10.79802,
                106.7245
            ],
            [
                10.79617,
                106.71908
            ],
            [
                10.79638,
                106.71935
            ],
            [
                10.7977,
                106.72017
            ],
            [
                10.79737,
                106.71988
            ],
            [
                10.79662,
                106.71917
            ],
            [
                10.79629,
                106.71886
            ],
            [
                10.79594,
                106.71864
            ],
            [
                10.78905,
                106.71455
            ],
            [
                10.78895,
                106.71493
            ],
            [
                10.78893,
                106.71536
            ],
            [
                10.78896,
                106.7157
            ],
            [
                10.78904,
                106.71599
            ],
            [
                10.78945,
                106.71606
            ],
            [
                10.78935,
                106.71573
            ],
            [
                10.78929,
                106.71533
            ],
            [
                10.78932,
                106.71481
            ],
            [
                10.78938,
                106.71437
            ],
            [
                10.78937,
                106.71398
            ],
            [
                10.78957,
                106.71107
            ],
            [
                10.78939,
                106.71068
            ],
            [
                10.7891,
                106.71025
            ],
            [
                10.78868,
                106.7099
            ],
            [
                10.78842,
                106.70975
            ],
            [
                10.78691,
                106.70905
            ],
            [
                10.786,
                106.70869
            ],
            [
                10.78573,
                106.70885
            ],
            [
                10.78531,
                106.70867
            ],
            [
                10.785,
                106.7085
            ],
            [
                10.78462,
                106.7082
            ],
            [
                10.78573,
                106.70885
            ],
            [
                10.7868,
                106.70936
            ]
        ],
        "nodes": [
            {
                "id": "node-21",
                "name": "Chân Cầu Sài Gòn",
                "lat": 10.79802,
                "lon": 106.7245,
                "latitude": 10.79802,
                "longitude": 106.7245,
                "base_water": 18.4,
                "water_level_cm": 18.4,
                "status": "SAFE"
            },
            {
                "id": "node-22",
                "name": "The Manor - Landmark 81",
                "lat": 10.78905,
                "lon": 106.71455,
                "latitude": 10.78905,
                "longitude": 106.71455,
                "base_water": 34.5,
                "water_level_cm": 34.5,
                "status": "ALERT"
            },
            {
                "id": "node-23",
                "name": "Rốn ngập Ung Văn Khiêm nối dài",
                "lat": 10.78932,
                "lon": 106.71481,
                "latitude": 10.78932,
                "longitude": 106.71481,
                "base_water": 46.0,
                "water_level_cm": 46.0,
                "status": "WARNING"
            },
            {
                "id": "node-24",
                "name": "Hầm chui Nguyễn Hữu Cảnh",
                "lat": 10.78691,
                "lon": 106.70905,
                "latitude": 10.78691,
                "longitude": 106.70905,
                "base_water": 36.8,
                "water_level_cm": 36.8,
                "status": "WARNING"
            },
            {
                "id": "node-25",
                "name": "Chân Cầu Thủ Thiêm 1",
                "lat": 10.7868,
                "lon": 106.70936,
                "latitude": 10.7868,
                "longitude": 106.70936,
                "base_water": 20.7,
                "water_level_cm": 20.7,
                "status": "ALERT"
            }
        ]
    },
    {
        "id": "road-06",
        "name": "Đường Ung Văn Khiêm",
        "district": "Bình Thạnh",
        "length_km": 2.8,
        "type": "ROAD",
        "base_water": 44.0,
        "max_water_cm": 44.0,
        "avg_water_cm": 29.9,
        "severity": "WARNING",
        "avoid_advice": "Ngập đoạn Bến xe Miền Đông cũ và ngã ba D2. Khuyên đi theo đường Bạch Đằng hoặc Đinh Bộ Lĩnh.",
        "coordinates": [
            [
                10.80993,
                106.71262
            ],
            [
                10.80929,
                106.71329
            ],
            [
                10.809,
                106.71366
            ],
            [
                10.80873,
                106.71407
            ],
            [
                10.80841,
                106.71459
            ],
            [
                10.80814,
                106.71513
            ],
            [
                10.80798,
                106.71545
            ],
            [
                10.80781,
                106.7159
            ],
            [
                10.80763,
                106.71637
            ],
            [
                10.80732,
                106.71747
            ],
            [
                10.80718,
                106.71801
            ],
            [
                10.80705,
                106.71856
            ],
            [
                10.80683,
                106.71935
            ],
            [
                10.80657,
                106.71983
            ],
            [
                10.8061,
                106.7204
            ],
            [
                10.80581,
                106.72069
            ],
            [
                10.8055,
                106.72093
            ],
            [
                10.80507,
                106.72115
            ],
            [
                10.80456,
                106.7214
            ],
            [
                10.8037,
                106.7217
            ],
            [
                10.80338,
                106.7219
            ],
            [
                10.80209,
                106.7226
            ],
            [
                10.8015,
                106.72294
            ],
            [
                10.80109,
                106.72317
            ],
            [
                10.80066,
                106.72345
            ],
            [
                10.80028,
                106.72358
            ],
            [
                10.79953,
                106.72366
            ],
            [
                10.79914,
                106.72392
            ]
        ],
        "nodes": [
            {
                "id": "node-26",
                "name": "Ngã tư Hàng Xanh",
                "lat": 10.80993,
                "lon": 106.71262,
                "latitude": 10.80993,
                "longitude": 106.71262,
                "base_water": 17.6,
                "water_level_cm": 17.6,
                "status": "SAFE"
            },
            {
                "id": "node-27",
                "name": "Đoạn Chu Văn An",
                "lat": 10.80781,
                "lon": 106.7159,
                "latitude": 10.80781,
                "longitude": 106.7159,
                "base_water": 33.0,
                "water_level_cm": 33.0,
                "status": "ALERT"
            },
            {
                "id": "node-28",
                "name": "Trước Bến xe Miền Đông",
                "lat": 10.8061,
                "lon": 106.7204,
                "latitude": 10.8061,
                "longitude": 106.7204,
                "base_water": 44.0,
                "water_level_cm": 44.0,
                "status": "WARNING"
            },
            {
                "id": "node-29",
                "name": "Chân Cầu Bình Triệu",
                "lat": 10.80209,
                "lon": 106.7226,
                "latitude": 10.80209,
                "longitude": 106.7226,
                "base_water": 35.2,
                "water_level_cm": 35.2,
                "status": "WARNING"
            },
            {
                "id": "node-30",
                "name": "Ngã ba Đường D2 (Nguyễn Gia Trí)",
                "lat": 10.79914,
                "lon": 106.72392,
                "latitude": 10.79914,
                "longitude": 106.72392,
                "base_water": 19.8,
                "water_level_cm": 19.8,
                "status": "SAFE"
            }
        ]
    }
]

ZONES_DATA: List[Dict[str, Any]] = [
    {
        "id": "zone-01",
        "name": "Khu vực Bán đảo Thảo Điền",
        "district": "TP. Thủ Đức",
        "type": "ZONE",
        "base_water": 54.0,
        "max_water_cm": 54.0,
        "avg_water_cm": 37.8,
        "severity": "CRITICAL",
        "area_km2": 3.8,
        "center": [
            10.8055,
            106.7325
        ],
        "polygon": [
            [
                10.8,
                106.732
            ],
            [
                10.803,
                106.738
            ],
            [
                10.81,
                106.739
            ],
            [
                10.816,
                106.734
            ],
            [
                10.814,
                106.726
            ],
            [
                10.806,
                106.726
            ],
            [
                10.8,
                106.732
            ]
        ],
        "avoid_advice": "Vùng bán đảo trũng thấp sát sông Sài Gòn ngập diện rộng. Tránh lưu thông vào trục Quốc Hương - Xuân Thủy.",
        "nodes": [
            {
                "id": "zone-01-node-01",
                "name": "Cổng vào Xa Lộ Hà Nội - Thảo Điền",
                "lat": 10.8015,
                "lon": 106.738,
                "latitude": 10.8015,
                "longitude": 106.738,
                "base_water": 20.0,
                "water_level_cm": 20.0,
                "status": "ALERT"
            },
            {
                "id": "zone-01-node-02",
                "name": "Giao lộ Xuân Thủy - Quốc Hương",
                "lat": 10.803,
                "lon": 106.7345,
                "latitude": 10.803,
                "longitude": 106.7345,
                "base_water": 38.0,
                "water_level_cm": 38.0,
                "status": "WARNING"
            },
            {
                "id": "zone-01-node-03",
                "name": "Rốn ngập trung tâm Quốc Hương",
                "lat": 10.8035,
                "lon": 106.7321,
                "latitude": 10.8035,
                "longitude": 106.7321,
                "base_water": 54.0,
                "water_level_cm": 54.0,
                "status": "CRITICAL"
            },
            {
                "id": "zone-01-node-04",
                "name": "Trường Quốc tế BIS Thảo Điền",
                "lat": 10.8075,
                "lon": 106.73,
                "latitude": 10.8075,
                "longitude": 106.73,
                "base_water": 45.0,
                "water_level_cm": 45.0,
                "status": "WARNING"
            },
            {
                "id": "zone-01-node-05",
                "name": "Bờ kè Nguyễn Văn Hưởng",
                "lat": 10.812,
                "lon": 106.728,
                "latitude": 10.812,
                "longitude": 106.728,
                "base_water": 32.0,
                "water_level_cm": 32.0,
                "status": "ALERT"
            }
        ]
    },
    {
        "id": "zone-02",
        "name": "Khu vực Thung lũng Chợ Thủ Đức",
        "district": "TP. Thủ Đức",
        "type": "ZONE",
        "base_water": 60.0,
        "max_water_cm": 60.0,
        "avg_water_cm": 39.6,
        "severity": "CRITICAL",
        "area_km2": 2.2,
        "center": [
            10.8525,
            106.7582
        ],
        "polygon": [
            [
                10.848,
                106.755
            ],
            [
                10.856,
                106.752
            ],
            [
                10.858,
                106.76
            ],
            [
                10.852,
                106.766
            ],
            [
                10.846,
                106.761
            ],
            [
                10.848,
                106.755
            ]
        ],
        "avoid_advice": "Lòng chảo tụ nước mưa đổ dồn từ dốc Đặng Thị Rành và Võ Văn Ngân. Cấm mọi phương tiện qua rốn Chợ.",
        "nodes": [
            {
                "id": "zone-02-node-01",
                "name": "Ngã 5 Thủ Đức - Kha Vạn Cân",
                "lat": 10.8495,
                "lon": 106.7625,
                "latitude": 10.8495,
                "longitude": 106.7625,
                "base_water": 26.0,
                "water_level_cm": 26.0,
                "status": "ALERT"
            },
            {
                "id": "zone-02-node-02",
                "name": "Dốc Dương Văn Cam",
                "lat": 10.851,
                "lon": 106.76,
                "latitude": 10.851,
                "longitude": 106.76,
                "base_water": 48.0,
                "water_level_cm": 48.0,
                "status": "WARNING"
            },
            {
                "id": "zone-02-node-03",
                "name": "Rốn trũng Chợ Thủ Đức",
                "lat": 10.8525,
                "lon": 106.7582,
                "latitude": 10.8525,
                "longitude": 106.7582,
                "base_water": 60.0,
                "water_level_cm": 60.0,
                "status": "CRITICAL"
            },
            {
                "id": "zone-02-node-04",
                "name": "Đặng Thị Rành - Tô Ngọc Vân",
                "lat": 10.8535,
                "lon": 106.7565,
                "latitude": 10.8535,
                "longitude": 106.7565,
                "base_water": 42.0,
                "water_level_cm": 42.0,
                "status": "WARNING"
            },
            {
                "id": "zone-02-node-05",
                "name": "Cầu Ngang - Võ Văn Ngân",
                "lat": 10.855,
                "lon": 106.7535,
                "latitude": 10.855,
                "longitude": 106.7535,
                "base_water": 22.0,
                "water_level_cm": 22.0,
                "status": "ALERT"
            }
        ]
    },
    {
        "id": "zone-03",
        "name": "Khu vực Trũng thấp Cây Trâm - Làng Hoa",
        "district": "Gò Vấp",
        "type": "ZONE",
        "base_water": 52.0,
        "max_water_cm": 52.0,
        "avg_water_cm": 34.8,
        "severity": "CRITICAL",
        "area_km2": 3.1,
        "center": [
            10.835,
            106.672
        ],
        "polygon": [
            [
                10.832,
                106.663
            ],
            [
                10.842,
                106.658
            ],
            [
                10.846,
                106.674
            ],
            [
                10.835,
                106.678
            ],
            [
                10.832,
                106.663
            ]
        ],
        "avoid_advice": "Rốn ngập do địa hình dốc tụ nước lưu vực Tham Lương. Tránh đi vào đường Nguyễn Văn Khối đoạn Làng Hoa.",
        "nodes": [
            {
                "id": "zone-03-node-01",
                "name": "Ngã ba Nguyễn Oanh - Lê Đức Thọ",
                "lat": 10.844,
                "lon": 106.679,
                "latitude": 10.844,
                "longitude": 106.679,
                "base_water": 20.0,
                "water_level_cm": 20.0,
                "status": "ALERT"
            },
            {
                "id": "zone-03-node-02",
                "name": "Lê Đức Thọ - Thống Nhất",
                "lat": 10.84,
                "lon": 106.675,
                "latitude": 10.84,
                "longitude": 106.675,
                "base_water": 36.0,
                "water_level_cm": 36.0,
                "status": "WARNING"
            },
            {
                "id": "zone-03-node-03",
                "name": "Rốn ngập Cây Trâm - Nguyễn Văn Khối",
                "lat": 10.835,
                "lon": 106.672,
                "latitude": 10.835,
                "longitude": 106.672,
                "base_water": 52.0,
                "water_level_cm": 52.0,
                "status": "CRITICAL"
            },
            {
                "id": "zone-03-node-04",
                "name": "Khu vực Công viên Làng Hoa",
                "lat": 10.8385,
                "lon": 106.666,
                "latitude": 10.8385,
                "longitude": 106.666,
                "base_water": 42.0,
                "water_level_cm": 42.0,
                "status": "WARNING"
            },
            {
                "id": "zone-03-node-05",
                "name": "Nguyễn Văn Khối - Lê Văn Thọ",
                "lat": 10.841,
                "lon": 106.661,
                "latitude": 10.841,
                "longitude": 106.661,
                "base_water": 24.0,
                "water_level_cm": 24.0,
                "status": "ALERT"
            }
        ]
    },
    {
        "id": "zone-04",
        "name": "Khu vực Lưu vực Bến Mễ Cốc - Hồ Học Lãm",
        "district": "Bình Tân & Q.8",
        "type": "ZONE",
        "base_water": 55.0,
        "max_water_cm": 55.0,
        "avg_water_cm": 37.8,
        "severity": "CRITICAL",
        "area_km2": 4.5,
        "center": [
            10.718,
            106.6185
        ],
        "polygon": [
            [
                10.706,
                106.62
            ],
            [
                10.725,
                106.61
            ],
            [
                10.73,
                106.622
            ],
            [
                10.716,
                106.634
            ],
            [
                10.706,
                106.62
            ]
        ],
        "avoid_advice": "Triều cường dâng Kênh Đôi ngập bờ kè Bến Phú Định & Hồ Học Lãm. Xe máy tuyệt đối tránh đi vào sát mép kênh.",
        "nodes": [
            {
                "id": "zone-04-node-01",
                "name": "Bờ kè Bến Phú Định",
                "lat": 10.71,
                "lon": 106.628,
                "latitude": 10.71,
                "longitude": 106.628,
                "base_water": 28.0,
                "water_level_cm": 28.0,
                "status": "ALERT"
            },
            {
                "id": "zone-04-node-02",
                "name": "Cầu Mỹ Thuận - An Dương Vương",
                "lat": 10.714,
                "lon": 106.623,
                "latitude": 10.714,
                "longitude": 106.623,
                "base_water": 44.0,
                "water_level_cm": 44.0,
                "status": "WARNING"
            },
            {
                "id": "zone-04-node-03",
                "name": "Rốn ngập Hồ Học Lãm",
                "lat": 10.718,
                "lon": 106.6185,
                "latitude": 10.718,
                "longitude": 106.6185,
                "base_water": 55.0,
                "water_level_cm": 55.0,
                "status": "CRITICAL"
            },
            {
                "id": "zone-04-node-04",
                "name": "Nút giao Đại lộ Võ Văn Kiệt",
                "lat": 10.723,
                "lon": 106.615,
                "latitude": 10.723,
                "longitude": 106.615,
                "base_water": 40.0,
                "water_level_cm": 40.0,
                "status": "WARNING"
            },
            {
                "id": "zone-04-node-05",
                "name": "Kinh Dương Vương - Vòng xoay An Lạc",
                "lat": 10.731,
                "lon": 106.611,
                "latitude": 10.731,
                "longitude": 106.611,
                "base_water": 22.0,
                "water_level_cm": 22.0,
                "status": "ALERT"
            }
        ]
    }
]

ALL_50_STATIONS: List[Dict[str, Any]] = [
    {
        "node_num": 1,
        "device_id": "VN-HCM-001",
        "device_name": "Sensor Station 01 (Ngã ba Trường Chinh)",
        "parent_id": "road-01",
        "parent_name": "Đường Phan Huy Ích",
        "parent_type": "ROAD",
        "district": "Gò Vấp - Tân Bình",
        "station_node": "Ngã ba Trường Chinh",
        "segment_idx": 0,
        "lat": 10.82346,
        "lon": 106.62943,
        "latitude": 10.82346,
        "longitude": 106.62943,
        "base_water": 20.8,
        "water_level_cm": 20.8,
        "status": "ALERT"
    },
    {
        "node_num": 2,
        "device_id": "VN-HCM-002",
        "device_name": "Sensor Station 02 (Đoạn giao Tây Thạnh)",
        "parent_id": "road-01",
        "parent_name": "Đường Phan Huy Ích",
        "parent_type": "ROAD",
        "district": "Gò Vấp - Tân Bình",
        "station_node": "Đoạn giao Tây Thạnh",
        "segment_idx": 1,
        "lat": 10.82712,
        "lon": 106.6315,
        "latitude": 10.82712,
        "longitude": 106.6315,
        "base_water": 39.0,
        "water_level_cm": 39.0,
        "status": "WARNING"
    },
    {
        "node_num": 3,
        "device_id": "VN-HCM-003",
        "device_name": "Sensor Station 03 (Rốn ngập Cầu Hy Vọng)",
        "parent_id": "road-01",
        "parent_name": "Đường Phan Huy Ích",
        "parent_type": "ROAD",
        "district": "Gò Vấp - Tân Bình",
        "station_node": "Rốn ngập Cầu Hy Vọng",
        "segment_idx": 2,
        "lat": 10.83283,
        "lon": 106.63422,
        "latitude": 10.83283,
        "longitude": 106.63422,
        "base_water": 52.0,
        "water_level_cm": 52.0,
        "status": "CRITICAL"
    },
    {
        "node_num": 4,
        "device_id": "VN-HCM-004",
        "device_name": "Sensor Station 04 (Đoạn giao Huỳnh Văn Nghệ)",
        "parent_id": "road-01",
        "parent_name": "Đường Phan Huy Ích",
        "parent_type": "ROAD",
        "district": "Gò Vấp - Tân Bình",
        "station_node": "Đoạn giao Huỳnh Văn Nghệ",
        "segment_idx": 3,
        "lat": 10.83905,
        "lon": 106.63708,
        "latitude": 10.83905,
        "longitude": 106.63708,
        "base_water": 41.6,
        "water_level_cm": 41.6,
        "status": "WARNING"
    },
    {
        "node_num": 5,
        "device_id": "VN-HCM-005",
        "device_name": "Sensor Station 05 (Ngã ba Quang Trung)",
        "parent_id": "road-01",
        "parent_name": "Đường Phan Huy Ích",
        "parent_type": "ROAD",
        "district": "Gò Vấp - Tân Bình",
        "station_node": "Ngã ba Quang Trung",
        "segment_idx": 4,
        "lat": 10.84429,
        "lon": 106.64011,
        "latitude": 10.84429,
        "longitude": 106.64011,
        "base_water": 23.4,
        "water_level_cm": 23.4,
        "status": "ALERT"
    },
    {
        "node_num": 6,
        "device_id": "VN-HCM-006",
        "device_name": "Sensor Station 06 (Cầu Tham Lương - Trường Chinh)",
        "parent_id": "road-02",
        "parent_name": "Đường Nguyễn Văn Quá",
        "parent_type": "ROAD",
        "district": "Quận 12",
        "station_node": "Cầu Tham Lương - Trường Chinh",
        "segment_idx": 0,
        "lat": 10.82783,
        "lon": 106.62674,
        "latitude": 10.82783,
        "longitude": 106.62674,
        "base_water": 20.0,
        "water_level_cm": 20.0,
        "status": "ALERT"
    },
    {
        "node_num": 7,
        "device_id": "VN-HCM-007",
        "device_name": "Sensor Station 07 (Giao lộ Đông Hưng Thuận)",
        "parent_id": "road-02",
        "parent_name": "Đường Nguyễn Văn Quá",
        "parent_type": "ROAD",
        "district": "Quận 12",
        "station_node": "Giao lộ Đông Hưng Thuận",
        "segment_idx": 1,
        "lat": 10.83544,
        "lon": 106.62882,
        "latitude": 10.83544,
        "longitude": 106.62882,
        "base_water": 37.5,
        "water_level_cm": 37.5,
        "status": "WARNING"
    },
    {
        "node_num": 8,
        "device_id": "VN-HCM-008",
        "device_name": "Sensor Station 08 (Rốn ngập Chợ Cầu)",
        "parent_id": "road-02",
        "parent_name": "Đường Nguyễn Văn Quá",
        "parent_type": "ROAD",
        "district": "Quận 12",
        "station_node": "Rốn ngập Chợ Cầu",
        "segment_idx": 2,
        "lat": 10.84278,
        "lon": 106.63091,
        "latitude": 10.84278,
        "longitude": 106.63091,
        "base_water": 50.0,
        "water_level_cm": 50.0,
        "status": "CRITICAL"
    },
    {
        "node_num": 9,
        "device_id": "VN-HCM-009",
        "device_name": "Sensor Station 09 (Đoạn giao Tô Ký)",
        "parent_id": "road-02",
        "parent_name": "Đường Nguyễn Văn Quá",
        "parent_type": "ROAD",
        "district": "Quận 12",
        "station_node": "Đoạn giao Tô Ký",
        "segment_idx": 3,
        "lat": 10.84979,
        "lon": 106.63654,
        "latitude": 10.84979,
        "longitude": 106.63654,
        "base_water": 40.0,
        "water_level_cm": 40.0,
        "status": "WARNING"
    },
    {
        "node_num": 10,
        "device_id": "VN-HCM-010",
        "device_name": "Sensor Station 10 (Ngã ba QL1A Tân Thới Hiệp)",
        "parent_id": "road-02",
        "parent_name": "Đường Nguyễn Văn Quá",
        "parent_type": "ROAD",
        "district": "Quận 12",
        "station_node": "Ngã ba QL1A Tân Thới Hiệp",
        "segment_idx": 4,
        "lat": 10.85647,
        "lon": 106.63941,
        "latitude": 10.85647,
        "longitude": 106.63941,
        "base_water": 22.5,
        "water_level_cm": 22.5,
        "status": "ALERT"
    },
    {
        "node_num": 11,
        "device_id": "VN-HCM-011",
        "device_name": "Sensor Station 11 (Chân cầu Tân Thuận)",
        "parent_id": "road-03",
        "parent_name": "Đường Huỳnh Tấn Phát",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Chân cầu Tân Thuận",
        "segment_idx": 0,
        "lat": 10.73791,
        "lon": 106.73034,
        "latitude": 10.73791,
        "longitude": 106.73034,
        "base_water": 22.4,
        "water_level_cm": 22.4,
        "status": "ALERT"
    },
    {
        "node_num": 12,
        "device_id": "VN-HCM-012",
        "device_name": "Sensor Station 12 (Ngã tư Nguyễn Thị Thập)",
        "parent_id": "road-03",
        "parent_name": "Đường Huỳnh Tấn Phát",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Ngã tư Nguyễn Thị Thập",
        "segment_idx": 1,
        "lat": 10.74141,
        "lon": 106.7298,
        "latitude": 10.74141,
        "longitude": 106.7298,
        "base_water": 42.0,
        "water_level_cm": 42.0,
        "status": "WARNING"
    },
    {
        "node_num": 13,
        "device_id": "VN-HCM-013",
        "device_name": "Sensor Station 13 (Rốn ngập Trần Trọng Cung)",
        "parent_id": "road-03",
        "parent_name": "Đường Huỳnh Tấn Phát",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Rốn ngập Trần Trọng Cung",
        "segment_idx": 2,
        "lat": 10.74375,
        "lon": 106.72954,
        "latitude": 10.74375,
        "longitude": 106.72954,
        "base_water": 56.0,
        "water_level_cm": 56.0,
        "status": "CRITICAL"
    },
    {
        "node_num": 14,
        "device_id": "VN-HCM-014",
        "device_name": "Sensor Station 14 (Chân cầu Phú Mỹ)",
        "parent_id": "road-03",
        "parent_name": "Đường Huỳnh Tấn Phát",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Chân cầu Phú Mỹ",
        "segment_idx": 3,
        "lat": 10.74832,
        "lon": 106.72887,
        "latitude": 10.74832,
        "longitude": 106.72887,
        "base_water": 44.8,
        "water_level_cm": 44.8,
        "status": "WARNING"
    },
    {
        "node_num": 15,
        "device_id": "VN-HCM-015",
        "device_name": "Sensor Station 15 (Chân cầu Phú Xuân)",
        "parent_id": "road-03",
        "parent_name": "Đường Huỳnh Tấn Phát",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Chân cầu Phú Xuân",
        "segment_idx": 4,
        "lat": 10.75265,
        "lon": 106.72855,
        "latitude": 10.75265,
        "longitude": 106.72855,
        "base_water": 25.2,
        "water_level_cm": 25.2,
        "status": "ALERT"
    },
    {
        "node_num": 16,
        "device_id": "VN-HCM-016",
        "device_name": "Sensor Station 16 (Chân cầu Tân Thuận 2)",
        "parent_id": "road-04",
        "parent_name": "Đường Trần Xuân Soạn",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Chân cầu Tân Thuận 2",
        "segment_idx": 0,
        "lat": 10.75101,
        "lon": 106.69107,
        "latitude": 10.75101,
        "longitude": 106.69107,
        "base_water": 21.2,
        "water_level_cm": 21.2,
        "status": "ALERT"
    },
    {
        "node_num": 17,
        "device_id": "VN-HCM-017",
        "device_name": "Sensor Station 17 (Bờ kè Lâm Văn Bền)",
        "parent_id": "road-04",
        "parent_name": "Đường Trần Xuân Soạn",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Bờ kè Lâm Văn Bền",
        "segment_idx": 1,
        "lat": 10.75172,
        "lon": 106.69849,
        "latitude": 10.75172,
        "longitude": 106.69849,
        "base_water": 39.8,
        "water_level_cm": 39.8,
        "status": "WARNING"
    },
    {
        "node_num": 18,
        "device_id": "VN-HCM-018",
        "device_name": "Sensor Station 18 (Rốn ngập Cầu Kênh Tẻ)",
        "parent_id": "road-04",
        "parent_name": "Đường Trần Xuân Soạn",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Rốn ngập Cầu Kênh Tẻ",
        "segment_idx": 2,
        "lat": 10.7518,
        "lon": 106.70669,
        "latitude": 10.7518,
        "longitude": 106.70669,
        "base_water": 53.0,
        "water_level_cm": 53.0,
        "status": "CRITICAL"
    },
    {
        "node_num": 19,
        "device_id": "VN-HCM-019",
        "device_name": "Sensor Station 19 (Chân cầu Rạch Ông)",
        "parent_id": "road-04",
        "parent_name": "Đường Trần Xuân Soạn",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Chân cầu Rạch Ông",
        "segment_idx": 3,
        "lat": 10.75189,
        "lon": 106.71725,
        "latitude": 10.75189,
        "longitude": 106.71725,
        "base_water": 42.4,
        "water_level_cm": 42.4,
        "status": "WARNING"
    },
    {
        "node_num": 20,
        "device_id": "VN-HCM-020",
        "device_name": "Sensor Station 20 (Chân cầu Chữ Y)",
        "parent_id": "road-04",
        "parent_name": "Đường Trần Xuân Soạn",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Chân cầu Chữ Y",
        "segment_idx": 4,
        "lat": 10.75749,
        "lon": 106.72229,
        "latitude": 10.75749,
        "longitude": 106.72229,
        "base_water": 23.9,
        "water_level_cm": 23.9,
        "status": "ALERT"
    },
    {
        "node_num": 21,
        "device_id": "VN-HCM-021",
        "device_name": "Sensor Station 21 (Chân Cầu Sài Gòn)",
        "parent_id": "road-05",
        "parent_name": "Đường Nguyễn Hữu Cảnh",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Chân Cầu Sài Gòn",
        "segment_idx": 0,
        "lat": 10.79802,
        "lon": 106.7245,
        "latitude": 10.79802,
        "longitude": 106.7245,
        "base_water": 18.4,
        "water_level_cm": 18.4,
        "status": "SAFE"
    },
    {
        "node_num": 22,
        "device_id": "VN-HCM-022",
        "device_name": "Sensor Station 22 (The Manor - Landmark 81)",
        "parent_id": "road-05",
        "parent_name": "Đường Nguyễn Hữu Cảnh",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "The Manor - Landmark 81",
        "segment_idx": 1,
        "lat": 10.78905,
        "lon": 106.71455,
        "latitude": 10.78905,
        "longitude": 106.71455,
        "base_water": 34.5,
        "water_level_cm": 34.5,
        "status": "ALERT"
    },
    {
        "node_num": 23,
        "device_id": "VN-HCM-023",
        "device_name": "Sensor Station 23 (Rốn ngập Ung Văn Khiêm nối dài)",
        "parent_id": "road-05",
        "parent_name": "Đường Nguyễn Hữu Cảnh",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Rốn ngập Ung Văn Khiêm nối dài",
        "segment_idx": 2,
        "lat": 10.78932,
        "lon": 106.71481,
        "latitude": 10.78932,
        "longitude": 106.71481,
        "base_water": 46.0,
        "water_level_cm": 46.0,
        "status": "WARNING"
    },
    {
        "node_num": 24,
        "device_id": "VN-HCM-024",
        "device_name": "Sensor Station 24 (Hầm chui Nguyễn Hữu Cảnh)",
        "parent_id": "road-05",
        "parent_name": "Đường Nguyễn Hữu Cảnh",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Hầm chui Nguyễn Hữu Cảnh",
        "segment_idx": 3,
        "lat": 10.78691,
        "lon": 106.70905,
        "latitude": 10.78691,
        "longitude": 106.70905,
        "base_water": 36.8,
        "water_level_cm": 36.8,
        "status": "WARNING"
    },
    {
        "node_num": 25,
        "device_id": "VN-HCM-025",
        "device_name": "Sensor Station 25 (Chân Cầu Thủ Thiêm 1)",
        "parent_id": "road-05",
        "parent_name": "Đường Nguyễn Hữu Cảnh",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Chân Cầu Thủ Thiêm 1",
        "segment_idx": 4,
        "lat": 10.7868,
        "lon": 106.70936,
        "latitude": 10.7868,
        "longitude": 106.70936,
        "base_water": 20.7,
        "water_level_cm": 20.7,
        "status": "ALERT"
    },
    {
        "node_num": 26,
        "device_id": "VN-HCM-026",
        "device_name": "Sensor Station 26 (Ngã tư Hàng Xanh)",
        "parent_id": "road-06",
        "parent_name": "Đường Ung Văn Khiêm",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Ngã tư Hàng Xanh",
        "segment_idx": 0,
        "lat": 10.80993,
        "lon": 106.71262,
        "latitude": 10.80993,
        "longitude": 106.71262,
        "base_water": 17.6,
        "water_level_cm": 17.6,
        "status": "SAFE"
    },
    {
        "node_num": 27,
        "device_id": "VN-HCM-027",
        "device_name": "Sensor Station 27 (Đoạn Chu Văn An)",
        "parent_id": "road-06",
        "parent_name": "Đường Ung Văn Khiêm",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Đoạn Chu Văn An",
        "segment_idx": 1,
        "lat": 10.80781,
        "lon": 106.7159,
        "latitude": 10.80781,
        "longitude": 106.7159,
        "base_water": 33.0,
        "water_level_cm": 33.0,
        "status": "ALERT"
    },
    {
        "node_num": 28,
        "device_id": "VN-HCM-028",
        "device_name": "Sensor Station 28 (Trước Bến xe Miền Đông)",
        "parent_id": "road-06",
        "parent_name": "Đường Ung Văn Khiêm",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Trước Bến xe Miền Đông",
        "segment_idx": 2,
        "lat": 10.8061,
        "lon": 106.7204,
        "latitude": 10.8061,
        "longitude": 106.7204,
        "base_water": 44.0,
        "water_level_cm": 44.0,
        "status": "WARNING"
    },
    {
        "node_num": 29,
        "device_id": "VN-HCM-029",
        "device_name": "Sensor Station 29 (Chân Cầu Bình Triệu)",
        "parent_id": "road-06",
        "parent_name": "Đường Ung Văn Khiêm",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Chân Cầu Bình Triệu",
        "segment_idx": 3,
        "lat": 10.80209,
        "lon": 106.7226,
        "latitude": 10.80209,
        "longitude": 106.7226,
        "base_water": 35.2,
        "water_level_cm": 35.2,
        "status": "WARNING"
    },
    {
        "node_num": 30,
        "device_id": "VN-HCM-030",
        "device_name": "Sensor Station 30 (Ngã ba Đường D2 (Nguyễn Gia Trí))",
        "parent_id": "road-06",
        "parent_name": "Đường Ung Văn Khiêm",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Ngã ba Đường D2 (Nguyễn Gia Trí)",
        "segment_idx": 4,
        "lat": 10.79914,
        "lon": 106.72392,
        "latitude": 10.79914,
        "longitude": 106.72392,
        "base_water": 19.8,
        "water_level_cm": 19.8,
        "status": "SAFE"
    },
    {
        "node_num": 31,
        "device_id": "VN-HCM-031",
        "device_name": "Sensor Station 31 (Cổng vào Xa Lộ Hà Nội - Thảo Điền)",
        "parent_id": "zone-01",
        "parent_name": "Khu vực Bán đảo Thảo Điền",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Cổng vào Xa Lộ Hà Nội - Thảo Điền",
        "segment_idx": 0,
        "lat": 10.8015,
        "lon": 106.738,
        "latitude": 10.8015,
        "longitude": 106.738,
        "base_water": 20.0,
        "water_level_cm": 20.0,
        "status": "ALERT"
    },
    {
        "node_num": 32,
        "device_id": "VN-HCM-032",
        "device_name": "Sensor Station 32 (Giao lộ Xuân Thủy - Quốc Hương)",
        "parent_id": "zone-01",
        "parent_name": "Khu vực Bán đảo Thảo Điền",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Giao lộ Xuân Thủy - Quốc Hương",
        "segment_idx": 1,
        "lat": 10.803,
        "lon": 106.7345,
        "latitude": 10.803,
        "longitude": 106.7345,
        "base_water": 38.0,
        "water_level_cm": 38.0,
        "status": "WARNING"
    },
    {
        "node_num": 33,
        "device_id": "VN-HCM-033",
        "device_name": "Sensor Station 33 (Rốn ngập trung tâm Quốc Hương)",
        "parent_id": "zone-01",
        "parent_name": "Khu vực Bán đảo Thảo Điền",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Rốn ngập trung tâm Quốc Hương",
        "segment_idx": 2,
        "lat": 10.8035,
        "lon": 106.7321,
        "latitude": 10.8035,
        "longitude": 106.7321,
        "base_water": 54.0,
        "water_level_cm": 54.0,
        "status": "CRITICAL"
    },
    {
        "node_num": 34,
        "device_id": "VN-HCM-034",
        "device_name": "Sensor Station 34 (Trường Quốc tế BIS Thảo Điền)",
        "parent_id": "zone-01",
        "parent_name": "Khu vực Bán đảo Thảo Điền",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Trường Quốc tế BIS Thảo Điền",
        "segment_idx": 3,
        "lat": 10.8075,
        "lon": 106.73,
        "latitude": 10.8075,
        "longitude": 106.73,
        "base_water": 45.0,
        "water_level_cm": 45.0,
        "status": "WARNING"
    },
    {
        "node_num": 35,
        "device_id": "VN-HCM-035",
        "device_name": "Sensor Station 35 (Bờ kè Nguyễn Văn Hưởng)",
        "parent_id": "zone-01",
        "parent_name": "Khu vực Bán đảo Thảo Điền",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Bờ kè Nguyễn Văn Hưởng",
        "segment_idx": 4,
        "lat": 10.812,
        "lon": 106.728,
        "latitude": 10.812,
        "longitude": 106.728,
        "base_water": 32.0,
        "water_level_cm": 32.0,
        "status": "ALERT"
    },
    {
        "node_num": 36,
        "device_id": "VN-HCM-036",
        "device_name": "Sensor Station 36 (Ngã 5 Thủ Đức - Kha Vạn Cân)",
        "parent_id": "zone-02",
        "parent_name": "Khu vực Thung lũng Chợ Thủ Đức",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Ngã 5 Thủ Đức - Kha Vạn Cân",
        "segment_idx": 0,
        "lat": 10.8495,
        "lon": 106.7625,
        "latitude": 10.8495,
        "longitude": 106.7625,
        "base_water": 26.0,
        "water_level_cm": 26.0,
        "status": "ALERT"
    },
    {
        "node_num": 37,
        "device_id": "VN-HCM-037",
        "device_name": "Sensor Station 37 (Dốc Dương Văn Cam)",
        "parent_id": "zone-02",
        "parent_name": "Khu vực Thung lũng Chợ Thủ Đức",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Dốc Dương Văn Cam",
        "segment_idx": 1,
        "lat": 10.851,
        "lon": 106.76,
        "latitude": 10.851,
        "longitude": 106.76,
        "base_water": 48.0,
        "water_level_cm": 48.0,
        "status": "WARNING"
    },
    {
        "node_num": 38,
        "device_id": "VN-HCM-038",
        "device_name": "Sensor Station 38 (Rốn trũng Chợ Thủ Đức)",
        "parent_id": "zone-02",
        "parent_name": "Khu vực Thung lũng Chợ Thủ Đức",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Rốn trũng Chợ Thủ Đức",
        "segment_idx": 2,
        "lat": 10.8525,
        "lon": 106.7582,
        "latitude": 10.8525,
        "longitude": 106.7582,
        "base_water": 60.0,
        "water_level_cm": 60.0,
        "status": "CRITICAL"
    },
    {
        "node_num": 39,
        "device_id": "VN-HCM-039",
        "device_name": "Sensor Station 39 (Đặng Thị Rành - Tô Ngọc Vân)",
        "parent_id": "zone-02",
        "parent_name": "Khu vực Thung lũng Chợ Thủ Đức",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Đặng Thị Rành - Tô Ngọc Vân",
        "segment_idx": 3,
        "lat": 10.8535,
        "lon": 106.7565,
        "latitude": 10.8535,
        "longitude": 106.7565,
        "base_water": 42.0,
        "water_level_cm": 42.0,
        "status": "WARNING"
    },
    {
        "node_num": 40,
        "device_id": "VN-HCM-040",
        "device_name": "Sensor Station 40 (Cầu Ngang - Võ Văn Ngân)",
        "parent_id": "zone-02",
        "parent_name": "Khu vực Thung lũng Chợ Thủ Đức",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Cầu Ngang - Võ Văn Ngân",
        "segment_idx": 4,
        "lat": 10.855,
        "lon": 106.7535,
        "latitude": 10.855,
        "longitude": 106.7535,
        "base_water": 22.0,
        "water_level_cm": 22.0,
        "status": "ALERT"
    },
    {
        "node_num": 41,
        "device_id": "VN-HCM-041",
        "device_name": "Sensor Station 41 (Ngã ba Nguyễn Oanh - Lê Đức Thọ)",
        "parent_id": "zone-03",
        "parent_name": "Khu vực Trũng thấp Cây Trâm - Làng Hoa",
        "parent_type": "ZONE",
        "district": "Gò Vấp",
        "station_node": "Ngã ba Nguyễn Oanh - Lê Đức Thọ",
        "segment_idx": 0,
        "lat": 10.844,
        "lon": 106.679,
        "latitude": 10.844,
        "longitude": 106.679,
        "base_water": 20.0,
        "water_level_cm": 20.0,
        "status": "ALERT"
    },
    {
        "node_num": 42,
        "device_id": "VN-HCM-042",
        "device_name": "Sensor Station 42 (Lê Đức Thọ - Thống Nhất)",
        "parent_id": "zone-03",
        "parent_name": "Khu vực Trũng thấp Cây Trâm - Làng Hoa",
        "parent_type": "ZONE",
        "district": "Gò Vấp",
        "station_node": "Lê Đức Thọ - Thống Nhất",
        "segment_idx": 1,
        "lat": 10.84,
        "lon": 106.675,
        "latitude": 10.84,
        "longitude": 106.675,
        "base_water": 36.0,
        "water_level_cm": 36.0,
        "status": "WARNING"
    },
    {
        "node_num": 43,
        "device_id": "VN-HCM-043",
        "device_name": "Sensor Station 43 (Rốn ngập Cây Trâm - Nguyễn Văn Khối)",
        "parent_id": "zone-03",
        "parent_name": "Khu vực Trũng thấp Cây Trâm - Làng Hoa",
        "parent_type": "ZONE",
        "district": "Gò Vấp",
        "station_node": "Rốn ngập Cây Trâm - Nguyễn Văn Khối",
        "segment_idx": 2,
        "lat": 10.835,
        "lon": 106.672,
        "latitude": 10.835,
        "longitude": 106.672,
        "base_water": 52.0,
        "water_level_cm": 52.0,
        "status": "CRITICAL"
    },
    {
        "node_num": 44,
        "device_id": "VN-HCM-044",
        "device_name": "Sensor Station 44 (Khu vực Công viên Làng Hoa)",
        "parent_id": "zone-03",
        "parent_name": "Khu vực Trũng thấp Cây Trâm - Làng Hoa",
        "parent_type": "ZONE",
        "district": "Gò Vấp",
        "station_node": "Khu vực Công viên Làng Hoa",
        "segment_idx": 3,
        "lat": 10.8385,
        "lon": 106.666,
        "latitude": 10.8385,
        "longitude": 106.666,
        "base_water": 42.0,
        "water_level_cm": 42.0,
        "status": "WARNING"
    },
    {
        "node_num": 45,
        "device_id": "VN-HCM-045",
        "device_name": "Sensor Station 45 (Nguyễn Văn Khối - Lê Văn Thọ)",
        "parent_id": "zone-03",
        "parent_name": "Khu vực Trũng thấp Cây Trâm - Làng Hoa",
        "parent_type": "ZONE",
        "district": "Gò Vấp",
        "station_node": "Nguyễn Văn Khối - Lê Văn Thọ",
        "segment_idx": 4,
        "lat": 10.841,
        "lon": 106.661,
        "latitude": 10.841,
        "longitude": 106.661,
        "base_water": 24.0,
        "water_level_cm": 24.0,
        "status": "ALERT"
    },
    {
        "node_num": 46,
        "device_id": "VN-HCM-046",
        "device_name": "Sensor Station 46 (Bờ kè Bến Phú Định)",
        "parent_id": "zone-04",
        "parent_name": "Khu vực Lưu vực Bến Mễ Cốc - Hồ Học Lãm",
        "parent_type": "ZONE",
        "district": "Bình Tân & Q.8",
        "station_node": "Bờ kè Bến Phú Định",
        "segment_idx": 0,
        "lat": 10.71,
        "lon": 106.628,
        "latitude": 10.71,
        "longitude": 106.628,
        "base_water": 28.0,
        "water_level_cm": 28.0,
        "status": "ALERT"
    },
    {
        "node_num": 47,
        "device_id": "VN-HCM-047",
        "device_name": "Sensor Station 47 (Cầu Mỹ Thuận - An Dương Vương)",
        "parent_id": "zone-04",
        "parent_name": "Khu vực Lưu vực Bến Mễ Cốc - Hồ Học Lãm",
        "parent_type": "ZONE",
        "district": "Bình Tân & Q.8",
        "station_node": "Cầu Mỹ Thuận - An Dương Vương",
        "segment_idx": 1,
        "lat": 10.714,
        "lon": 106.623,
        "latitude": 10.714,
        "longitude": 106.623,
        "base_water": 44.0,
        "water_level_cm": 44.0,
        "status": "WARNING"
    },
    {
        "node_num": 48,
        "device_id": "VN-HCM-048",
        "device_name": "Sensor Station 48 (Rốn ngập Hồ Học Lãm)",
        "parent_id": "zone-04",
        "parent_name": "Khu vực Lưu vực Bến Mễ Cốc - Hồ Học Lãm",
        "parent_type": "ZONE",
        "district": "Bình Tân & Q.8",
        "station_node": "Rốn ngập Hồ Học Lãm",
        "segment_idx": 2,
        "lat": 10.718,
        "lon": 106.6185,
        "latitude": 10.718,
        "longitude": 106.6185,
        "base_water": 55.0,
        "water_level_cm": 55.0,
        "status": "CRITICAL"
    },
    {
        "node_num": 49,
        "device_id": "VN-HCM-049",
        "device_name": "Sensor Station 49 (Nút giao Đại lộ Võ Văn Kiệt)",
        "parent_id": "zone-04",
        "parent_name": "Khu vực Lưu vực Bến Mễ Cốc - Hồ Học Lãm",
        "parent_type": "ZONE",
        "district": "Bình Tân & Q.8",
        "station_node": "Nút giao Đại lộ Võ Văn Kiệt",
        "segment_idx": 3,
        "lat": 10.723,
        "lon": 106.615,
        "latitude": 10.723,
        "longitude": 106.615,
        "base_water": 40.0,
        "water_level_cm": 40.0,
        "status": "WARNING"
    },
    {
        "node_num": 50,
        "device_id": "VN-HCM-050",
        "device_name": "Sensor Station 50 (Kinh Dương Vương - Vòng xoay An Lạc)",
        "parent_id": "zone-04",
        "parent_name": "Khu vực Lưu vực Bến Mễ Cốc - Hồ Học Lãm",
        "parent_type": "ZONE",
        "district": "Bình Tân & Q.8",
        "station_node": "Kinh Dương Vương - Vòng xoay An Lạc",
        "segment_idx": 4,
        "lat": 10.731,
        "lon": 106.611,
        "latitude": 10.731,
        "longitude": 106.611,
        "base_water": 22.0,
        "water_level_cm": 22.0,
        "status": "ALERT"
    }
]


class ThingsBoardService:
    def __init__(self):
        self.jwt_token: Optional[str] = None
        self.token_expiry: float = 0
        self.tb_client = httpx.AsyncClient(timeout=4.0)

    async def _get_auth_token(self) -> Optional[str]:
        if self.jwt_token and time.time() < self.token_expiry:
            return self.jwt_token

        # Only connect to the endpoint configured for this environment.
        urls_to_try = [settings.THINGSBOARD_URL]

        for base_url in urls_to_try:
            try:
                login_url = f"{base_url.rstrip('/')}/api/auth/login"
                resp = await self.tb_client.post(login_url, json={
                    "username": settings.THINGSBOARD_USERNAME,
                    "password": settings.THINGSBOARD_PASSWORD
                })
                if resp.status_code == 200:
                    data = resp.json()
                    self.jwt_token = data.get("token")
                    self.token_expiry = time.time() + 3600
                    return self.jwt_token
            except Exception:
                continue

        return None

    async def _fetch_devices_from_tb(self) -> Optional[List[DeviceTelemetry]]:
        token = await self._get_auth_token()
        if not token:
            return None

        headers = {"X-Authorization": f"Bearer {token}"}
        base_url = settings.THINGSBOARD_URL.rstrip('/')

        try:
            resp = await self.tb_client.get(
                f"{base_url}/api/tenant/devices?pageSize=100&page=0",
                headers=headers
            )
            if resp.status_code != 200:
                return None

            device_list = resp.json().get("data", [])
            if not device_list:
                return None

            results: List[DeviceTelemetry] = []
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for idx, dev in enumerate(device_list):
                dev_id = dev["id"]["id"]
                dev_name = dev["name"]

                matched_station = ALL_50_STATIONS[idx % len(ALL_50_STATIONS)]

                lat, lon, water, rain, temp = matched_station["lat"], matched_station["lon"], matched_station["base_water"], 25.0, 30.0
                telemetry_resp = await self.tb_client.get(
                    f"{base_url}/api/plugins/telemetry/DEVICE/{dev_id}/values/timeseries",
                    headers=headers
                )
                
                if telemetry_resp.status_code == 200:
                    t_data = telemetry_resp.json()
                    if "latitude" in t_data:
                        lat = float(t_data["latitude"][0]["value"])
                    if "longitude" in t_data:
                        lon = float(t_data["longitude"][0]["value"])
                    if "water_level_cm" in t_data:
                        water = float(t_data["water_level_cm"][0]["value"])
                    if "rainfall_mm" in t_data:
                        rain = float(t_data["rainfall_mm"][0]["value"])
                    if "temperature_c" in t_data:
                        temp = float(t_data["temperature_c"][0]["value"])

                status = "CRITICAL" if water >= 50.0 else ("WARNING" if water >= 35.0 else ("ALERT" if water >= 20.0 else "SAFE"))

                results.append(DeviceTelemetry(
                    device_id=dev_id,
                    name=dev_name,
                    latitude=round(lat, 5),
                    longitude=round(lon, 5),
                    water_level_cm=round(water, 1),
                    rainfall_mm=round(rain, 1),
                    temperature_c=round(temp, 1),
                    status=status,
                    updated_at=now_str,
                    road_id=matched_station["parent_id"] if matched_station["parent_type"] == "ROAD" else None,
                    road_name=matched_station["parent_name"] if matched_station["parent_type"] == "ROAD" else None,
                    station_node=matched_station["station_node"],
                    segment_idx=matched_station["segment_idx"],
                    parent_id=matched_station["parent_id"],
                    parent_name=matched_station["parent_name"],
                    parent_type=matched_station["parent_type"]
                ))

            if results:
                return results
        except Exception:
            pass

        return None

    async def get_live_devices(self) -> List[DeviceTelemetry]:
        real_devices = await self._fetch_devices_from_tb()
        if real_devices and len(real_devices) >= 50:
            return real_devices

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_list: List[DeviceTelemetry] = []

        for st in ALL_50_STATIONS:
            fluctuation = (random.random() - 0.5) * 4.0
            water_val = round(max(5.0, st["base_water"] + fluctuation), 1)
            status = "CRITICAL" if water_val >= 50.0 else ("WARNING" if water_val >= 35.0 else ("ALERT" if water_val >= 20.0 else "SAFE"))

            updated_list.append(DeviceTelemetry(
                device_id=st["device_id"],
                name=st["device_name"],
                latitude=round(st["lat"], 5),
                longitude=round(st["lon"], 5),
                water_level_cm=water_val,
                rainfall_mm=round(random.uniform(15.0, 42.0), 1),
                temperature_c=round(random.uniform(28.0, 31.5), 1),
                status=status,
                updated_at=now_str,
                road_id=st["parent_id"] if st["parent_type"] == "ROAD" else None,
                road_name=st["parent_name"] if st["parent_type"] == "ROAD" else None,
                station_node=st["station_node"],
                segment_idx=st["segment_idx"],
                parent_id=st["parent_id"],
                parent_name=st["parent_name"],
                parent_type=st["parent_type"]
            ))

        return updated_list

    def get_city_summary(self, devices: List[DeviceTelemetry]) -> CitySummary:
        safe_c = sum(1 for d in devices if d.status == "SAFE")
        alert_c = sum(1 for d in devices if d.status in ("ALERT", "WARNING"))
        crit_c = sum(1 for d in devices if d.status == "CRITICAL")
        avg_w = round(sum(d.water_level_cm for d in devices) / len(devices), 1) if devices else 0.0
        return CitySummary(
            safe_count=safe_c,
            alert_count=alert_c,
            critical_count=crit_c,
            avg_water_level_cm=avg_w,
            total_active_devices=len(devices)
        )

    def get_flooded_roads(self, devices: List[DeviceTelemetry]) -> List[FloodedRoad]:
        device_by_segment = {
            (d.parent_id, d.segment_idx): d for d in devices if d.parent_id and d.segment_idx is not None
        }

        roads_result: List[FloodedRoad] = []
        for road in ROADS_DATA:
            road_id = road["id"]
            node_water_levels: List[float] = []
            road_nodes: List[RoadNode] = []

            for idx, n in enumerate(road["nodes"]):
                telemetry = device_by_segment.get((road_id, idx))
                if telemetry:
                    w = telemetry.water_level_cm
                    s = telemetry.status
                else:
                    w = n["base_water"]
                    s = "CRITICAL" if w >= 50.0 else ("WARNING" if w >= 35.0 else ("ALERT" if w >= 20.0 else "SAFE"))

                node_water_levels.append(w)
                road_nodes.append(RoadNode(
                    id=n["id"],
                    name=n["name"],
                    latitude=n["lat"],
                    longitude=n["lon"],
                    water_level_cm=round(w, 1),
                    status=s
                ))

            avg_w = round(sum(node_water_levels) / len(node_water_levels), 1) if node_water_levels else 0.0
            max_w = round(max(node_water_levels), 1) if node_water_levels else 0.0
            severity = "CRITICAL" if max_w >= 50.0 else ("WARNING" if max_w >= 35.0 else ("ALERT" if max_w >= 20.0 else "SAFE"))

            roads_result.append(FloodedRoad(
                id=road["id"],
                name=road["name"],
                district=road["district"],
                length_km=road["length_km"],
                severity=severity,
                avg_water_cm=avg_w,
                max_water_cm=max_w,
                avoid_advice=road.get("avoid_advice"),
                coordinates=road["coordinates"],
                nodes=road_nodes
            ))

        return roads_result

    def get_flood_zones(self, devices: List[DeviceTelemetry]) -> List[FloodZone]:
        device_by_segment = {
            (d.parent_id, d.segment_idx): d for d in devices if d.parent_id and d.segment_idx is not None
        }

        zones_result: List[FloodZone] = []
        for zone in ZONES_DATA:
            zone_id = zone["id"]
            node_water_levels: List[float] = []
            zone_nodes: List[RoadNode] = []

            for idx, n in enumerate(zone["nodes"]):
                telemetry = device_by_segment.get((zone_id, idx))
                if telemetry:
                    w = telemetry.water_level_cm
                    s = telemetry.status
                else:
                    w = n["base_water"]
                    s = "CRITICAL" if w >= 50.0 else ("WARNING" if w >= 35.0 else ("ALERT" if w >= 20.0 else "SAFE"))

                node_water_levels.append(w)
                zone_nodes.append(RoadNode(
                    id=f"{zone_id}-node-{idx+1}",
                    name=n["name"],
                    latitude=n["lat"],
                    longitude=n["lon"],
                    water_level_cm=round(w, 1),
                    status=s
                ))

            avg_w = round(sum(node_water_levels) / len(node_water_levels), 1) if node_water_levels else 0.0
            max_w = round(max(node_water_levels), 1) if node_water_levels else 0.0
            severity = "CRITICAL" if max_w >= 50.0 else ("WARNING" if max_w >= 35.0 else ("ALERT" if max_w >= 20.0 else "SAFE"))

            zones_result.append(FloodZone(
                id=zone["id"],
                name=zone["name"],
                district=zone["district"],
                area_km2=zone["area_km2"],
                severity=severity,
                avg_water_cm=avg_w,
                max_water_cm=max_w,
                center=zone["center"],
                polygon=zone["polygon"],
                avoid_advice=zone.get("avoid_advice"),
                nodes=zone_nodes
            ))

        return zones_result

    @staticmethod
    def get_severe_locations() -> List[SevereLocation]:
        locs: List[SevereLocation] = []
        for r in ROADS_DATA:
            center_node = r["nodes"][2]
            locs.append(SevereLocation(
                id=r["id"],
                name=r["name"],
                district=r["district"],
                water_level_m=round(center_node["base_water"] / 100.0, 2),
                severity="CRITICAL" if center_node["base_water"] >= 50.0 else "WARNING",
                minutes_ago=random.randint(1, 5),
                latitude=center_node["lat"],
                longitude=center_node["lon"]
            ))
        for z in ZONES_DATA:
            locs.append(SevereLocation(
                id=z["id"],
                name=z["name"],
                district=z["district"],
                water_level_m=round(z["base_water"] / 100.0, 2),
                severity="CRITICAL" if z["base_water"] >= 50.0 else "WARNING",
                minutes_ago=random.randint(1, 5),
                latitude=z["center"][0],
                longitude=z["center"][1]
            ))
        return locs


tb_service = ThingsBoardService()
