# tests/test_kernel.py
from unittest.mock import MagicMock
from backend.agent.kernel import AgentKernel


def maak_kernel(stop_reason="end_turn", tool_calls=None):
    llm = MagicMock()
    harness = MagicMock()
    harness.execute.return_value = {"result": "ok"}

    # Mock LLM response
    if stop_reason == "end_turn":
        tekst_block = MagicMock()
        tekst_block.text = "Test antwoord."
        tekst_block.type = "text"
        response = MagicMock()
        response.stop_reason = "end_turn"
        response.content = [tekst_block]
    elif stop_reason == "tool_use":
        tool_block = MagicMock()
        tool_block.type = "tool_use"
        tool_block.name = "get_student_data"
        tool_block.input = {"studentnummer": "20240001"}
        tool_block.id = "tool-id-1"
        eind_block = MagicMock()
        eind_block.text = "Antwoord na tool."
        eind_block.type = "text"
        eind_response = MagicMock()
        eind_response.stop_reason = "end_turn"
        eind_response.content = [eind_block]
        between_response = MagicMock()
        between_response.stop_reason = "tool_use"
        between_response.content = [tool_block]
        llm.chat.side_effect = [between_response, eind_response]
        kernel = AgentKernel(llm=llm, harness=harness)
        return kernel
    elif stop_reason == "onbekend":
        response = MagicMock()
        response.stop_reason = "max_tokens"
        response.content = []

    llm.chat.return_value = response
    return AgentKernel(llm=llm, harness=harness)


def test_end_turn_geeft_tekst_terug():
    kernel = maak_kernel("end_turn")
    result = kernel.run("Test vraag")
    assert result == "Test antwoord."


def test_tool_use_roept_harness_aan():
    kernel = maak_kernel("tool_use")
    result = kernel.run("Hoe staat student 20240001 ervoor?")
    kernel.harness.execute.assert_called_once_with(
        "get_student_data", {"studentnummer": "20240001"}, kernel.harness.execute.call_args[0][2]
    )
    assert result == "Antwoord na tool."


def test_onbekende_stop_reason_geeft_foutmelding():
    kernel = maak_kernel("onbekend")
    result = kernel.run("Test")
    assert "Onverwachte stop_reason" in result


def test_sessie_id_wordt_aangemaakt_als_none():
    kernel = maak_kernel("end_turn")
    result = kernel.run("Test", sessie_id=None)
    assert result == "Test antwoord."
