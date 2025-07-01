#!/usr/bin/env python3
"""
Phase 3: ドローン物理シミュレーションデモスクリプト
Tello EDU ダミーシステムの3D物理シミュレーション機能のデモンストレーション
"""

import time
import logging
import argparse
from typing import Optional

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.drone_simulator import (
    DroneSimulator, MultiDroneSimulator, Vector3D, Obstacle, ObstacleType
)
from core.virtual_camera import (
    VirtualCameraStream, TrackingObject, TrackingObjectType, MovementPattern
)
from config.simulation_config import ConfigurationManager


# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_basic_flight_simulation():
    """基本飛行シミュレーションデモ"""
    print("\n" + "="*60)
    print("基本飛行シミュレーションデモ")
    print("="*60)
    
    # ドローンシミュレータを作成
    simulator = DroneSimulator("demo_drone", (15.0, 15.0, 8.0))
    
    # カメラストリームを統合
    camera = VirtualCameraStream(640, 480, 30)
    
    # 追跡対象を追加
    person = TrackingObject(
        TrackingObjectType.PERSON,
        (200, 300),
        (40, 80),
        (0, 255, 0),
        MovementPattern.SINE_WAVE,
        velocity=20.0,
        amplitude=100.0,
        frequency=0.05
    )
    camera.add_tracking_object(person)
    
    vehicle = TrackingObject(
        TrackingObjectType.VEHICLE,
        (400, 200),
        (60, 30),
        (255, 0, 0),
        MovementPattern.CIRCULAR,
        velocity=15.0
    )
    camera.add_tracking_object(vehicle)
    
    simulator.set_camera_stream(camera)
    
    # サンプル障害物を追加
    simulator.add_sample_obstacles()
    
    # シミュレーション開始
    simulator.start_simulation()
    
    try:
        print("ドローンシミュレーション開始...")
        
        # 離陸
        print("離陸中...")
        success = simulator.takeoff()
        if success:
            print("✅ 離陸成功")
        else:
            print("❌ 離陸失敗")
            return
        
        # 離陸完了まで待機
        time.sleep(2.0)
        
        # 手動で飛行状態に設定（デモ用）
        simulator.current_state.state = simulator.current_state.state.__class__.FLYING
        print("✅ 飛行状態に移行")
        
        # 複数の位置に移動
        waypoints = [
            (3.0, 3.0, 2.0),
            (3.0, -3.0, 3.0),
            (-3.0, -3.0, 2.5),
            (-3.0, 3.0, 2.0),
            (0.0, 0.0, 2.0)
        ]
        
        for i, (x, y, z) in enumerate(waypoints):
            print(f"ウェイポイント {i+1}: ({x}, {y}, {z}) へ移動...")
            success = simulator.move_to_position(x, y, z)
            if success:
                print(f"✅ ウェイポイント {i+1} 設定成功")
            else:
                print(f"❌ ウェイポイント {i+1} 設定失敗")
            
            # 移動時間を待機
            time.sleep(1.5)
            
            # 回転テスト
            yaw_angle = (i + 1) * 45
            print(f"回転: {yaw_angle}度...")
            simulator.rotate_to_yaw(yaw_angle)
            time.sleep(0.5)
        
        # 現在の統計情報を表示
        stats = simulator.get_statistics()
        print("\n現在の統計情報:")
        print(f"  位置: {stats['current_position']}")
        print(f"  速度: {stats['current_velocity']}")
        print(f"  バッテリー: {stats['battery_level']:.1f}%")
        print(f"  飛行時間: {stats['total_flight_time']:.1f}秒")
        print(f"  移動距離: {stats['total_distance_traveled']:.2f}m")
        
        # カメラストリーム統計
        if simulator.camera_stream:
            camera_stats = simulator.camera_stream.get_statistics()
            print(f"  カメラFPS: {camera_stats['actual_fps']:.1f}")
            print(f"  フレーム数: {camera_stats['frame_count']}")
        
        # 着陸
        print("\n着陸中...")
        success = simulator.land()
        if success:
            print("✅ 着陸開始")
        else:
            print("❌ 着陸失敗")
        
        time.sleep(2.0)
        print("✅ デモ完了")
        
    finally:
        # シミュレーション停止
        simulator.stop_simulation()
        print("シミュレーション停止")


def demo_obstacle_avoidance():
    """障害物回避デモ"""
    print("\n" + "="*60)
    print("障害物回避シミュレーションデモ")
    print("="*60)
    
    # 障害物コースシナリオを使用
    config_manager = ConfigurationManager()
    config = config_manager.get_preset_scenario("obstacle_course")
    
    simulator = DroneSimulator("obstacle_drone", config.space_bounds)
    
    # 設定から障害物を追加
    for obs_config in config.obstacles:
        obstacle = Obstacle(
            id=obs_config.obstacle_id,
            obstacle_type=ObstacleType(obs_config.obstacle_type),
            position=Vector3D(*obs_config.position),
            size=Vector3D(*obs_config.size),
            is_static=obs_config.is_static
        )
        simulator.virtual_world.add_obstacle(obstacle)
    
    # カメラストリーム設定
    camera = VirtualCameraStream(640, 480, 30)
    
    # 複数の追跡対象を追加
    tracking_objects = [
        TrackingObject(
            TrackingObjectType.PERSON,
            (150, 200),
            (30, 60),
            (0, 255, 0),
            MovementPattern.RANDOM_WALK,
            velocity=10.0
        ),
        TrackingObject(
            TrackingObjectType.BOX,
            (450, 300),
            (40, 40),
            (150, 75, 0),
            MovementPattern.LINEAR,
            velocity=8.0,
            angle=45.0
        ),
        TrackingObject(
            TrackingObjectType.BALL,
            (320, 240),
            (25, 25),
            (255, 255, 0),
            MovementPattern.CIRCULAR,
            velocity=12.0
        )
    ]
    
    for obj in tracking_objects:
        camera.add_tracking_object(obj)
    
    simulator.set_camera_stream(camera)
    simulator.start_simulation()
    
    try:
        print("障害物回避シミュレーション開始...")
        
        # 初期位置設定
        simulator.current_state.position = Vector3D(-5.0, -5.0, 0.1)
        
        # 離陸
        print("離陸中...")
        success = simulator.takeoff()
        if success:
            print("✅ 離陸成功")
            time.sleep(2.0)
            simulator.current_state.state = simulator.current_state.state.__class__.FLYING
        
        # 障害物を避けながら移動するパス
        safe_waypoints = [
            (-2.0, -2.0, 2.0),  # 安全な位置へ
            (0.0, -4.0, 2.0),   # 柱を避けて
            (4.0, -2.0, 2.0),   # 箱の周りを回る
            (4.0, 2.0, 3.0),    # 高度を上げて
            (0.0, 4.0, 2.5),    # 低い天井部分を避けて
            (-4.0, 2.0, 2.0),   # 反対側へ
            (0.0, 0.0, 2.0)     # 中央に戻る
        ]
        
        for i, (x, y, z) in enumerate(safe_waypoints):
            print(f"安全ルート {i+1}: ({x}, {y}, {z}) へ移動...")
            
            # 目標位置が安全かチェック
            target_pos = Vector3D(x, y, z)
            if simulator.virtual_world.is_position_valid(target_pos):
                success = simulator.move_to_position(x, y, z)
                if success:
                    print(f"✅ 安全ルート {i+1} 設定成功")
                else:
                    print(f"❌ 安全ルート {i+1} 設定失敗")
            else:
                print(f"⚠️  安全ルート {i+1} は障害物と衝突の可能性があります")
                continue
            
            time.sleep(1.5)
        
        # 統計情報表示
        stats = simulator.get_statistics()
        print(f"\n障害物回避デモ結果:")
        print(f"  衝突回数: {stats['collision_count']}")
        print(f"  障害物数: {stats['obstacle_count']}")
        print(f"  飛行時間: {stats['total_flight_time']:.1f}秒")
        
        # 着陸
        simulator.land()
        time.sleep(2.0)
        print("✅ 障害物回避デモ完了")
        
    finally:
        simulator.stop_simulation()


def demo_multi_drone_simulation():
    """複数ドローンシミュレーションデモ"""
    print("\n" + "="*60)
    print("複数ドローンシミュレーションデモ")
    print("="*60)
    
    # 複数ドローンシミュレータを作成
    multi_sim = MultiDroneSimulator((25.0, 25.0, 12.0))
    
    # 3台のドローンを追加
    drones = {}
    drone_configs = [
        ("patrol_drone_1", (-8.0, -8.0, 0.1), (255, 0, 0)),
        ("patrol_drone_2", (8.0, -8.0, 0.1), (0, 255, 0)),
        ("survey_drone", (0.0, 8.0, 0.1), (0, 0, 255))
    ]
    
    for drone_id, initial_pos, color in drone_configs:
        drone = multi_sim.add_drone(drone_id, initial_pos)
        
        # 各ドローンにカメラストリームを設定
        camera = VirtualCameraStream(320, 240, 20)
        
        # ドローンごとに異なる追跡対象
        if "patrol" in drone_id:
            tracking_obj = TrackingObject(
                TrackingObjectType.PERSON,
                (100, 150),
                (25, 50),
                color,
                MovementPattern.LINEAR,
                velocity=15.0,
                angle=90.0 if "1" in drone_id else 270.0
            )
        else:  # survey_drone
            tracking_obj = TrackingObject(
                TrackingObjectType.VEHICLE,
                (160, 120),
                (35, 20),
                color,
                MovementPattern.CIRCULAR,
                velocity=10.0
            )
        
        camera.add_tracking_object(tracking_obj)
        drone.set_camera_stream(camera)
        drones[drone_id] = drone
    
    # 倉庫環境を設定（障害物追加）
    warehouse_obstacles = [
        ("rack_1", ObstacleType.DYNAMIC, (5.0, 0.0, 2.0), (2.0, 8.0, 4.0)),
        ("rack_2", ObstacleType.DYNAMIC, (-5.0, 0.0, 2.0), (2.0, 8.0, 4.0)),
        ("conveyor", ObstacleType.DYNAMIC, (0.0, 0.0, 0.5), (1.0, 12.0, 1.0))
    ]
    
    for obs_id, obs_type, pos, size in warehouse_obstacles:
        obstacle = Obstacle(
            id=obs_id,
            obstacle_type=obs_type,
            position=Vector3D(*pos),
            size=Vector3D(*size)
        )
        multi_sim.shared_virtual_world.add_obstacle(obstacle)
    
    # 全シミュレーション開始
    multi_sim.start_all_simulations()
    
    try:
        print("複数ドローンシミュレーション開始...")
        
        # 全ドローン離陸
        for drone_id, drone in drones.items():
            print(f"{drone_id} 離陸中...")
            success = drone.takeoff()
            if success:
                print(f"✅ {drone_id} 離陸成功")
            time.sleep(0.5)
        
        time.sleep(3.0)  # 離陸完了待機
        
        # 各ドローンを飛行状態に設定
        for drone in drones.values():
            drone.current_state.state = drone.current_state.state.__class__.FLYING
        
        # パトロールミッション実行
        patrol_missions = {
            "patrol_drone_1": [
                (-6.0, -6.0, 3.0),
                (-6.0, 6.0, 3.0),
                (6.0, 6.0, 3.0),
                (6.0, -6.0, 3.0)
            ],
            "patrol_drone_2": [
                (6.0, -6.0, 4.0),
                (6.0, 6.0, 4.0),
                (-6.0, 6.0, 4.0),
                (-6.0, -6.0, 4.0)
            ],
            "survey_drone": [
                (0.0, 6.0, 5.0),
                (8.0, 0.0, 5.0),
                (0.0, -6.0, 5.0),
                (-8.0, 0.0, 5.0)
            ]
        }
        
        # ミッション実行
        max_waypoints = max(len(mission) for mission in patrol_missions.values())
        
        for waypoint_idx in range(max_waypoints):
            print(f"\nウェイポイント {waypoint_idx + 1} 実行中...")
            
            for drone_id, mission in patrol_missions.items():
                if waypoint_idx < len(mission):
                    x, y, z = mission[waypoint_idx]
                    drone = drones[drone_id]
                    success = drone.move_to_position(x, y, z)
                    if success:
                        print(f"  ✅ {drone_id}: ({x}, {y}, {z})")
                    else:
                        print(f"  ❌ {drone_id}: 移動失敗")
            
            time.sleep(2.0)
        
        # 統計情報表示
        print("\n=== 複数ドローンミッション結果 ===")
        all_stats = multi_sim.get_all_statistics()
        
        for drone_id, stats in all_stats.items():
            print(f"\n{drone_id}:")
            print(f"  位置: {stats['current_position']}")
            print(f"  バッテリー: {stats['battery_level']:.1f}%")
            print(f"  飛行時間: {stats['total_flight_time']:.1f}秒")
            print(f"  移動距離: {stats['total_distance_traveled']:.2f}m")
            print(f"  衝突回数: {stats['collision_count']}")
        
        # 全ドローン着陸
        print("\n全ドローン着陸中...")
        for drone_id, drone in drones.items():
            drone.land()
            print(f"✅ {drone_id} 着陸開始")
        
        time.sleep(3.0)
        print("✅ 複数ドローンデモ完了")
        
    finally:
        multi_sim.stop_all_simulations()


def demo_emergency_scenario():
    """緊急事態シナリオデモ"""
    print("\n" + "="*60)
    print("緊急事態シナリオデモ")
    print("="*60)
    
    config_manager = ConfigurationManager()
    config = config_manager.get_preset_scenario("emergency")
    
    simulator = DroneSimulator("emergency_drone", config.space_bounds)
    
    # 低バッテリー設定
    simulator.current_state.battery_level = 25.0
    
    # 緊急事態用の障害物追加
    for obs_config in config.obstacles:
        obstacle = Obstacle(
            id=obs_config.obstacle_id,
            obstacle_type=ObstacleType(obs_config.obstacle_type),
            position=Vector3D(*obs_config.position),
            size=Vector3D(*obs_config.size)
        )
        simulator.virtual_world.add_obstacle(obstacle)
    
    # 高速カメラストリーム
    camera = VirtualCameraStream(640, 480, 60)
    
    # 緊急事態の対象（動く人物）
    emergency_target = TrackingObject(
        TrackingObjectType.PERSON,
        (300, 200),
        (50, 100),
        (255, 0, 0),  # 赤色（緊急）
        MovementPattern.RANDOM_WALK,
        velocity=25.0  # 高速移動
    )
    camera.add_tracking_object(emergency_target)
    
    simulator.set_camera_stream(camera)
    simulator.start_simulation()
    
    try:
        print("緊急事態シナリオ開始...")
        print(f"初期バッテリー: {simulator.current_state.battery_level:.1f}%")
        
        # 緊急離陸
        print("緊急離陸中...")
        success = simulator.takeoff()
        if success:
            print("✅ 緊急離陸成功")
            time.sleep(1.5)
            simulator.current_state.state = simulator.current_state.state.__class__.FLYING
        
        # 緊急ミッション（高速・直線的な移動）
        emergency_waypoints = [
            (2.0, 3.0, 2.0),   # 倒れた木の近く
            (-3.0, -2.0, 4.0), # タワーの近く（高度を上げて）
            (1.0, 1.0, 2.0),   # 捜索ポイント
            (0.0, 0.0, 1.5)    # 緊急着陸地点
        ]
        
        for i, (x, y, z) in enumerate(emergency_waypoints):
            current_battery = simulator.current_state.battery_level
            print(f"緊急ポイント {i+1}: ({x}, {y}, {z}) - バッテリー: {current_battery:.1f}%")
            
            if current_battery < 10.0:
                print("⚠️  バッテリー危険レベル - 緊急着陸実行")
                simulator.emergency_land()
                break
            
            success = simulator.move_to_position(x, y, z)
            if success:
                print(f"✅ 緊急ポイント {i+1} 到達")
            else:
                print(f"❌ 緊急ポイント {i+1} 到達失敗")
            
            # バッテリーを手動で消費（デモ用）
            simulator.current_state.battery_level -= 5.0
            
            time.sleep(1.0)
        
        # 最終統計
        stats = simulator.get_statistics()
        print(f"\n緊急ミッション結果:")
        print(f"  最終バッテリー: {stats['battery_level']:.1f}%")
        print(f"  総飛行時間: {stats['total_flight_time']:.1f}秒")
        print(f"  総移動距離: {stats['total_distance_traveled']:.2f}m")
        print(f"  衝突回数: {stats['collision_count']}")
        
        if stats['battery_level'] > 0:
            print("✅ 緊急ミッション完了")
        else:
            print("⚠️  バッテリー切れによる緊急着陸")
        
    finally:
        simulator.stop_simulation()


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Phase 3 ドローン物理シミュレーションデモ')
    parser.add_argument(
        '--demo',
        choices=['basic', 'obstacle', 'multi', 'emergency', 'all'],
        default='all',
        help='実行するデモを選択'
    )
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='3D可視化を有効にする（要matplotlib）'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='ログレベル設定'
    )
    
    args = parser.parse_args()
    
    # ログレベル設定
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    print("🚁 Phase 3: Tello EDU ダミーシステム物理シミュレーションデモ")
    print("=" * 70)
    
    try:
        if args.demo == 'basic' or args.demo == 'all':
            demo_basic_flight_simulation()
        
        if args.demo == 'obstacle' or args.demo == 'all':
            demo_obstacle_avoidance()
        
        if args.demo == 'multi' or args.demo == 'all':
            demo_multi_drone_simulation()
        
        if args.demo == 'emergency' or args.demo == 'all':
            demo_emergency_scenario()
        
        print("\n" + "="*70)
        print("🎉 全デモンストレーション完了！")
        print("Phase 3の3D物理シミュレーション機能が正常に動作しています。")
        
    except KeyboardInterrupt:
        print("\n⚠️  デモが中断されました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        logger.exception("デモ実行中にエラーが発生")


if __name__ == "__main__":
    main()