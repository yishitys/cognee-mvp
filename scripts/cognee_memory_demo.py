import asyncio

import cognee


DATASET_NAME = "m_agents_hackathon"


async def main() -> None:
    await cognee.remember(
        """
        M-Agents hackathon project context:
        The pipeline has five sequential tasks: data ingestion, classification,
        reconciliation, narrative generation, and live interface demo.
        Cognee should be used as persistent memory so later agents can recall
        prior task context instead of starting from scratch.
        Sponsors include Trupeer, Cognee, PyMC Labs, Geodo, and Red Bull.
        Recommended build: a memory-native multi-agent ops pipeline that makes
        memory writes, recalls, provenance, and uncertainty visible to judges.
        """,
        dataset_name=DATASET_NAME,
    )

    response = await cognee.recall(
        query_text="What should the M-Agents hackathon project emphasize?",
        datasets=[DATASET_NAME],
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
