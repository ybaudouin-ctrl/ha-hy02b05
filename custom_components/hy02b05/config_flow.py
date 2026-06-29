"""Config flow for HY02B05."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import DEFAULT_NAME, DOMAIN


class HY02ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle first step."""

        if user_input is not None:

            await self.async_set_unique_id(
                user_input["topic"]
            )

            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input["name"],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "name",
                        default=DEFAULT_NAME,
                    ): str,

                    vol.Required(
                        "topic",
                        default="Therm_UG_Bureau",
                    ): str,
                }
            ),
        )
