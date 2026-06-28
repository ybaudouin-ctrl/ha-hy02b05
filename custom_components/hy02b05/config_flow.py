from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN


class HY02ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """HY02B05 Config Flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):

        if user_input is not None:

            return self.async_create_entry(
                title=user_input["name"],
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(
                    "name",
                    default="Thermostat Bureau",
                ): str,

                vol.Required(
                    "topic",
                    default="Therm_UG_Bureau",
                ): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )