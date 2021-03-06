/**
 * (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
 */
package com.hpe.krakenmare.repositories;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.util.Collections;
import java.util.UUID;

import org.apache.avro.util.Utf8;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import com.hpe.krakenmare.Main;
import com.hpe.krakenmare.core.Agent;

import redis.clients.jedis.HostAndPort;
import redis.clients.jedis.Jedis;

public class AgentMemoryRepositoryTest {

	private static Jedis jedis = null;
	private static AgentMemoryRepository repo = null;

	static Agent newAgent(String name) {
		String uid = name + "-" + System.currentTimeMillis();
		return new Agent(-1l, new Utf8(uid), UUID.randomUUID(), new Utf8(name), Collections.emptyList());
	}

	@BeforeEach
	void before() throws IOException {
		jedis = new Jedis(HostAndPort.parseString(Main.getProperty("redis.server")));
		repo = new AgentMemoryRepository();
	}

	@AfterEach
	void after() {
		repo = null;
		jedis.close();
		jedis = null;
	}

	@Test
	void testAdd() {
		Agent agent = repo.create(newAgent("myAgent"));
		assertTrue(repo.save(agent));
		assertEquals(1, repo.getAll().size());
		assertEquals(1, repo.count());
	}

	@Test
	void testDelete() {
		Agent agent1 = repo.create(newAgent("myAgent1"));
		assertTrue(repo.save(agent1));
		Agent agent2 = repo.create(newAgent("myAgent2"));
		assertTrue(repo.save(agent2));
		Agent agent3 = repo.create(newAgent("myAgent3"));
		assertTrue(repo.save(agent3));
		assertEquals(3, repo.getAll().size());
		assertEquals(3, repo.count());

		assertTrue(repo.delete(agent2));
		assertEquals(2, repo.getAll().size());
		assertEquals(2, repo.count());


		assertTrue(repo.delete(agent1));
		assertEquals(1, repo.getAll().size());
		assertEquals(1, repo.count());
	}

}
