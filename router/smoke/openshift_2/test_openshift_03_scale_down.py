import time
from messaging_components.routers import Dispatch
from messaging_components.routers.dispatch.management import RouterQuery
from iqa_common.executor import Command, Execution
from iqa_common.utils.openshift_util import OpenShiftUtil

MESH_SIZE = 3


def test_scale_down_router(router_cluster):
    """
    Scale down the number of PODs to 1.
    Expects that the scale down command completes successfully.
    :param router_cluster:
    :return:
    """
    router: Dispatch = router_cluster[0]
    cluster: str = router_cluster[1]
    token: str = router_cluster[2]

    # OCP Instance
    ocp = OpenShiftUtil(router.executor, 'https://%s:8443' % cluster, token)
    execution: Execution = ocp.scale(1, 'amq-interconnect')
    assert execution.completed_successfully()


def test_mesh_after_scale_down(router_cluster, iqa):
    """
    Queries the router to validate that the number of Nodes in the topology is 1.
    :param router_cluster:
    :return:
    """
    router: Dispatch = router_cluster[0]
    validate_mesh_size(router, 1 * len(iqa.get_routers()))


def validate_mesh_size(router_cluster: Dispatch, new_size: int):
    """
    Asserts that router topology size matches "new_size" value.
    :param router_cluster:
    :param new_size:
    :return:
    """
    time.sleep(90)
    query = RouterQuery(host=router_cluster.node.ip, port=router_cluster.port, router=router_cluster)
    node_list = query.node()
    assert len(node_list) == new_size
