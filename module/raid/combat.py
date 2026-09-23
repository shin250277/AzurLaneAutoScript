from module.combat.combat import Combat
from module.guild.assets import BATTLE_STATUS_CF, EXP_INFO_CF
from module.raid.kr_fleet import KR_RAID_EX_RESULT, KR_RAID_EX_EXP, KR_RAID_EX_CONFIRM


class RaidCombat(Combat):
    def handle_battle_status(self, drop=None):
        """
        Args:
            drop (DropImage):

        Returns:
            bool:
        """
        if self.is_combat_executing():
            return False
        if self.config.SERVER == 'kr' and self.appear_then_click(
                KR_RAID_EX_RESULT, offset=(5, 5), interval=2):
            return True
        if super().handle_battle_status(drop=drop):
            return True
        if self.appear(BATTLE_STATUS_CF, interval=self.battle_status_click_interval):
            if drop:
                drop.handle_add(self)
            else:
                self.device.sleep((0.25, 0.5))
            self.device.click(BATTLE_STATUS_CF)
            return True

        return False

    def handle_get_items(self, drop=None):
        """
        Args:
            drop (DropImage):

        Returns:
            bool:
        """
        if super().handle_get_items(drop=drop):
            self.interval_reset(BATTLE_STATUS_CF)
            return True
        else:
            return False

    def handle_exp_info(self):
        """
        Returns:
            bool:
        """
        if self.is_combat_executing():
            return False
        if self.config.SERVER == 'kr' and self.appear(KR_RAID_EX_EXP, offset=(5, 5)):
            if self.appear_then_click(KR_RAID_EX_CONFIRM, offset=(5, 5), interval=2):
                return True
        if super().handle_exp_info():
            return True
        if self.appear_then_click(EXP_INFO_CF):
            self.device.sleep((0.25, 0.5))
            return True

        return False
