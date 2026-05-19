from utils.patcher.src.patch import Patch

from patches.src.add_columns_to_job_opening import AddColumnsToJobOpening
from patches.src.add_liked_by_user_to_job import AddLikedByUserToJob
from patches.src.add_link_to_job_opening import AddLinkToJobOpening
from patches.src.add_public_id_to_job import AddPublicIdToJob

PATCHES: list[Patch] = [AddPublicIdToJob(), AddLikedByUserToJob(), AddColumnsToJobOpening(), AddLinkToJobOpening()]
